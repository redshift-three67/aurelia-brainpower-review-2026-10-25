const {spawn} = require('child_process');
const {randomUUID} = require('crypto');
const fs = require('fs');
const http = require('http');
const net = require('net');
const os = require('os');
const path = require('path');
const {performance} = require('perf_hooks');

const BROWSER_DIR = __dirname;
const WORKTREE_ROOT = path.resolve(BROWSER_DIR, '..', '..');
const REPOSITORY_ROOT = path.resolve(WORKTREE_ROOT, '..', '..');
const SERVER_SCRIPT = path.join(BROWSER_DIR, 'isolated_server.py');
const PROCESS_TREE_SUPERVISOR = path.join(BROWSER_DIR, 'process_tree_supervisor.py');
const TREE_TOKEN_ENV = 'MORPHIC_BROWSER_PROCESS_TREE_TOKEN';
const PLAYWRIGHT_CLI = path.join(
  BROWSER_DIR,
  'node_modules',
  '@playwright',
  'test',
  'cli.js',
);
const SHARD_COUNT = 4;
const DEFAULT_PLAYWRIGHT_TIMEOUT_MS = 15 * 60 * 1000;
const DEFAULT_PROCESS_TREE_TIMEOUT_MS = 10000;
const DEFAULT_READINESS_TIMEOUT_MS = 10000;
const MAX_READINESS_BYTES = 1024;
const READY_RECORD = {event: 'ready', schema_version: 1};
const READY_LINE = Buffer.from(JSON.stringify(READY_RECORD), 'utf8');
const activeSupervisors = new Set();
const activeRuntimeRoots = new Set();
const activeRunOperations = new Set();
const supervisorStates = new WeakMap();
const runtimeCleanupPromises = new Map();
let shuttingDown = false;
let shutdownPromise = null;

function existingPath(candidates) {
  return candidates.find(candidate => candidate && fs.existsSync(candidate));
}

function resolvePython() {
  return existingPath([
    process.env.PLAYWRIGHT_PYTHON,
    path.join(REPOSITORY_ROOT, '.venv', 'Scripts', 'python.exe'),
  ]) || 'python';
}

function resolveBrowser() {
  return existingPath([
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    process.env.LOCALAPPDATA
      ? path.join(process.env.LOCALAPPDATA, 'Google', 'Chrome', 'Application', 'chrome.exe')
      : null,
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  ]);
}

function cleanEnvironment(environment = process.env) {
  return Object.fromEntries(
    Object.entries(environment).filter(
      ([name]) => !name.toUpperCase().startsWith('MORPHIC_'),
    ),
  );
}

function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      server.close(error => {
        if (error) reject(error);
        else resolve(address.port);
      });
    });
  });
}

function buildServerEnv(runtimeRoot, port, healthToken) {
  return {
    ...cleanEnvironment(),
    MORPHIC_BROWSER_PORT: String(port),
    MORPHIC_BROWSER_RUNTIME_ROOT: runtimeRoot,
    MORPHIC_BROWSER_HEALTH_TOKEN: healthToken,
    MORPHIC_RUNTIME_DIR: path.join(runtimeRoot, 'runtime'),
    MORPHIC_HARMONIZATION_JOBS_DIR: path.join(runtimeRoot, 'harmonization-jobs'),
    MORPHIC_PARALLEL_EXPORT_ROOT: path.join(runtimeRoot, 'exports'),
    MORPHIC_OPERATOR_ID: 'browser-test-operator',
    MORPHIC_TENANT_ID: `browser-test-${process.pid}-${path.basename(runtimeRoot)}`,
    MORPHIC_GROUP_ANALYSIS_ENABLED: '0',
    MORPHIC_ADMIN_CATALOG_ENABLED: '0',
    OPENBLAS_NUM_THREADS: '1',
    PYTHONIOENCODING: 'utf-8',
    PYTHONUTF8: '1',
  };
}

function buildTestEnv(baseURL, browser) {
  return {
    ...cleanEnvironment(),
    PLAYWRIGHT_BASE_URL: baseURL,
    ...(browser ? {PLAYWRIGHT_CHROMIUM_EXECUTABLE: browser} : {}),
  };
}

function healthReady(url, expectedToken) {
  return new Promise(resolve => {
    const request = http.get(url, response => {
      let body = '';
      response.setEncoding('utf8');
      response.on('data', chunk => { body += chunk; });
      response.on('end', () => {
        try {
          const payload = JSON.parse(body);
          resolve(response.statusCode === 200 && payload.token === expectedToken);
        } catch (_error) {
          resolve(false);
        }
      });
    });
    request.setTimeout(1000, () => request.destroy());
    request.on('error', () => resolve(false));
  });
}

function supervisorFailure(supervisor) {
  const state = supervisorStates.get(supervisor);
  return state?.spawnError || state?.protocolError || null;
}

async function waitForHealth(url, healthToken, server, logs) {
  const deadline = Date.now() + 60000;
  while (Date.now() < deadline) {
    const failure = supervisorFailure(server);
    if (failure) throw failure;
    if (server.exitCode !== null) {
      throw new Error(`Testserver exited before readiness.\n${logs.text}`);
    }
    const ready = await healthReady(url, healthToken);
    const currentFailure = supervisorFailure(server);
    if (currentFailure) throw currentFailure;
    if (ready) return;
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  throw new Error(`Testserver did not become ready at ${url}.\n${logs.text}`);
}

function playwrightTimeoutMs(environment = process.env) {
  const configured = Number(environment.PLAYWRIGHT_CLI_TIMEOUT_MS);
  return Number.isFinite(configured) && configured > 0
    ? configured
    : DEFAULT_PLAYWRIGHT_TIMEOUT_MS;
}

function processTreeTimeoutMs(dependencies = {}) {
  const configured = dependencies.stopTimeoutMs;
  return Number.isFinite(configured) && configured > 0
    ? configured
    : DEFAULT_PROCESS_TREE_TIMEOUT_MS;
}

function readinessTimeoutMs(options = {}) {
  const configured = options.readinessTimeoutMs;
  return Number.isFinite(configured) && configured > 0
    ? configured
    : DEFAULT_READINESS_TIMEOUT_MS;
}

function readinessError(message, cause = undefined) {
  return new Error(
    `Supervisor readiness ${message}`,
    cause === undefined ? undefined : {cause},
  );
}

function outputForwarder(value) {
  if (typeof value === 'function') return value;
  return () => {};
}

function withTimeout(operation, timeoutMs, label) {
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    return Promise.reject(new Error(`${label} timed out`));
  }
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(
      () => {
        const error = new Error(`${label} timed out after ${timeoutMs}ms`);
        error.code = 'ETIMEDOUT';
        reject(error);
      },
      timeoutMs,
    );
    Promise.resolve(operation).then(
      value => {
        clearTimeout(timeout);
        resolve(value);
      },
      error => {
        clearTimeout(timeout);
        reject(error);
      },
    );
  });
}

function monotonicNow(dependencies = {}) {
  return dependencies.now || (() => performance.now());
}

function remaining(deadline, now) {
  return Math.max(0, deadline - now());
}

function stopDeadlineError() {
  const error = new Error('Supervisor stop deadline exhausted');
  error.code = 'ETIMEDOUT';
  return error;
}

function combinePrimaryAndCleanup(primary, cleanup) {
  if (!primary) return cleanup;
  if (!cleanup) return primary;
  return new AggregateError(
    [primary, cleanup],
    'Test group failed and cleanup also failed',
    {cause: primary},
  );
}

function flattenUniqueFailures(failures) {
  const flattened = [];
  const visit = failure => {
    if (failure instanceof AggregateError) {
      for (const nested of failure.errors) visit(nested);
    } else if (!flattened.includes(failure)) {
      flattened.push(failure);
    }
  };
  for (const failure of failures) visit(failure);
  return flattened;
}

function trackSupervisor(supervisor, options = {}, dependencies = {}) {
  const existing = supervisorStates.get(supervisor);
  if (existing) return supervisor;

  let resolveReady;
  let rejectReady;
  let resolveExit;
  let rejectExit;
  let rejectProtocol;
  let resolveProtocolSettlement;
  let rejectProtocolSettlement;
  const state = {
    dependencies,
    exited: false,
    closed: false,
    exitCode: null,
    spawnError: null,
    protocolError: null,
    protocolSettled: false,
    treeAbsenceProven: false,
    readinessBuffer: Buffer.alloc(0),
    readinessLine: null,
    readyAccepted: false,
    readySettled: false,
    stopPromise: null,
    stopWritten: false,
    onError: null,
    onExit: null,
    onClose: null,
    onReadyData: null,
    onReadyEnd: null,
    onReadyError: null,
    onReadyClose: null,
    protocolDataDetached: false,
    readyGuardDetached: false,
    released: false,
    release: null,
    controlError: null,
    controlWriteReject: null,
    onControlError: null,
    controlGuardAttached: false,
    readinessTimer: null,
    prepareForExit: null,
    readyPromise: new Promise((resolve, reject) => {
      resolveReady = resolve;
      rejectReady = reject;
    }),
    exitPromise: new Promise((resolve, reject) => {
      resolveExit = resolve;
      rejectExit = reject;
    }),
    protocolFailurePromise: new Promise((_resolve, reject) => {
      rejectProtocol = reject;
    }),
    protocolSettlementPromise: new Promise((resolve, reject) => {
      resolveProtocolSettlement = resolve;
      rejectProtocolSettlement = reject;
    }),
  };
  state.readyPromise.catch(() => {});
  state.exitPromise.catch(() => {});
  state.protocolFailurePromise.catch(() => {});
  state.protocolSettlementPromise.catch(() => {});

  const readyStream = supervisor.stdio?.[3];
  const forwardStdout = outputForwarder(options.onStdout);
  const forwardStderr = outputForwarder(options.onStderr);
  const settleReady = error => {
    if (state.readySettled) return;
    state.readySettled = true;
    clearTimeout(state.readinessTimer);
    if (error) rejectReady(error);
    else resolveReady();
  };
  const settleProtocol = error => {
    if (state.protocolSettled) return;
    state.protocolSettled = true;
    if (error) rejectProtocolSettlement(error);
    else resolveProtocolSettlement();
  };
  const detachProtocolData = () => {
    if (state.protocolDataDetached) return;
    state.protocolDataDetached = true;
    state.readinessBuffer = Buffer.alloc(0);
    state.readinessLine = null;
    readyStream?.removeListener?.('data', state.onReadyData);
    readyStream?.removeListener?.('end', state.onReadyEnd);
  };
  const detachReadyGuard = () => {
    if (state.readyGuardDetached) return;
    state.readyGuardDetached = true;
    readyStream?.removeListener?.('error', state.onReadyError);
    readyStream?.removeListener?.('close', state.onReadyClose);
  };
  const abortReadyStream = () => {
    detachProtocolData();
    if (typeof readyStream?.destroy === 'function' && !readyStream.destroyed) {
      readyStream.destroy();
    } else {
      readyStream?.resume?.();
    }
  };
  const failProtocol = error => {
    if (!state.protocolError) {
      state.protocolError = error;
      rejectProtocol(error);
    }
    settleProtocol(state.protocolError);
    abortReadyStream();
    settleReady(state.protocolError);
  };
  const cleanupListeners = () => {
    clearTimeout(state.readinessTimer);
    supervisor.removeListener('error', state.onError);
    supervisor.removeListener('exit', state.onExit);
    supervisor.removeListener('close', state.onClose);
    supervisor.stdout?.removeListener?.('data', forwardStdout);
    supervisor.stderr?.removeListener?.('data', forwardStderr);
    if (state.controlGuardAttached) {
      supervisor.stdin?.removeListener?.('error', state.onControlError);
      state.controlGuardAttached = false;
    }
    detachProtocolData();
    detachReadyGuard();
  };
  const release = () => {
    if (state.released) return;
    state.released = true;
    activeSupervisors.delete(supervisor);
    cleanupListeners();
  };
  state.release = release;
  state.prepareForExit = error => {
    settleReady(error);
    detachProtocolData();
    for (const stream of [supervisor.stdin, supervisor.stdout, supervisor.stderr, readyStream]) {
      stream?.unref?.();
    }
    supervisor.unref?.();
    try {
      if (!supervisor.stdin?.destroyed) supervisor.stdin?.destroy?.();
    } catch (_error) {
      // Process exit remains the final bounded decision.
    }
  };

  state.onReadyData = chunk => {
    const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    if (state.readinessLine !== null) {
      failProtocol(readinessError('contained trailing bytes'));
      return;
    }
    const newline = bytes.indexOf(10);
    if (newline < 0) {
      if (state.readinessBuffer.length + bytes.length > MAX_READINESS_BYTES) {
        failProtocol(readinessError('record exceeded the size limit'));
        return;
      }
      state.readinessBuffer = Buffer.concat([state.readinessBuffer, bytes]);
      return;
    }
    if (state.readinessBuffer.length + newline + 1 > MAX_READINESS_BYTES) {
      failProtocol(readinessError('record exceeded the size limit'));
      return;
    }
    if (newline + 1 !== bytes.length) {
      failProtocol(readinessError('contained trailing bytes'));
      return;
    }
    state.readinessLine = Buffer.concat([
      state.readinessBuffer,
      bytes.subarray(0, newline),
    ]);
    state.readinessBuffer = Buffer.alloc(0);
    if (!state.readinessLine.equals(READY_LINE)) {
      failProtocol(readinessError('record was not the accepted schema'));
      return;
    }
    state.readyAccepted = true;
    settleReady(null);
  };
  state.onReadyEnd = () => {
    if (state.readinessLine === null) {
      failProtocol(readinessError('ended before one complete record'));
      return;
    }
    detachProtocolData();
    settleProtocol(null);
  };
  state.onReadyError = error => {
    if (state.protocolError) return;
    failProtocol(readinessError('channel failed', error));
  };
  state.onReadyClose = () => {
    if (!state.protocolSettled) {
      if (state.readyAccepted && !state.protocolError) settleProtocol(null);
      else failProtocol(readinessError('channel closed before protocol settlement'));
    }
    detachReadyGuard();
  };
  state.onError = error => {
    state.spawnError = error;
    settleReady(error);
    settleProtocol(null);
  };
  state.onExit = code => {
    state.exited = true;
    state.exitCode = code;
  };
  state.onClose = code => {
    state.closed = true;
    if (!state.exited) {
      state.exited = true;
      state.exitCode = code;
    }
    state.treeAbsenceProven = Boolean(
      state.spawnError && supervisor.pid == null && !state.readyAccepted,
    );
    if (!state.readyAccepted && !state.protocolError && !state.spawnError) {
      failProtocol(readinessError('was not published before supervisor exit'));
    }
    if (!state.protocolSettled && state.readyAccepted && !state.protocolError) {
      settleProtocol(null);
    }
    if (state.spawnError && !state.treeAbsenceProven) rejectExit(state.spawnError);
    else if (state.treeAbsenceProven) resolveExit(0);
    else resolveExit(state.exitCode);
    release();
  };

  supervisorStates.set(supervisor, state);
  activeSupervisors.add(supervisor);
  supervisor.once('error', state.onError);
  supervisor.once('exit', state.onExit);
  supervisor.once('close', state.onClose);
  supervisor.stdout?.on?.('data', forwardStdout);
  supervisor.stderr?.on?.('data', forwardStderr);
  readyStream?.on?.('error', state.onReadyError);
  readyStream?.on?.('close', state.onReadyClose);
  readyStream?.on?.('data', state.onReadyData);
  readyStream?.on?.('end', state.onReadyEnd);
  state.readinessTimer = setTimeout(
    () => failProtocol(readinessError('timed out')),
    readinessTimeoutMs(options),
  );
  if (!readyStream) failProtocol(readinessError('channel is unavailable'));
  if (supervisor.exitCode !== null || supervisor.signalCode !== null) {
    state.exited = true;
    state.exitCode = supervisor.exitCode;
  }
  return supervisor;
}

function spawnSupervised(command, args, options = {}, dependencies = {}) {
  const spawnProcess = dependencies.spawn || spawn;
  const uuid = dependencies.randomUUID || randomUUID;
  const treeToken = uuid().replaceAll('-', '');
  const {
    onStdout,
    onStderr,
    stdout = 'pipe',
    stderr = 'pipe',
    readinessTimeoutMs: configuredReadinessTimeout,
    ...spawnOptions
  } = options;
  const supervisor = spawnProcess(
    dependencies.python || resolvePython(),
    [PROCESS_TREE_SUPERVISOR, '--ready-fd', '3', '--', command, ...args],
    {
      ...spawnOptions,
      env: {...(spawnOptions.env || {}), [TREE_TOKEN_ENV]: treeToken},
      stdio: ['pipe', stdout, stderr, 'pipe'],
      detached: false,
    },
  );
  return trackSupervisor(
    supervisor,
    {
      onStdout,
      onStderr,
      readinessTimeoutMs: configuredReadinessTimeout,
    },
    dependencies,
  );
}

function waitForSupervisorReady(supervisor) {
  const state = supervisorStates.get(supervisor);
  if (!state) return Promise.reject(new Error('Supervisor is not tracked'));
  return state.readyPromise;
}

function waitForExit(child, timeoutMs = null, label = 'Process') {
  if (!child) return Promise.resolve(null);
  if (child.exitCode !== null) return Promise.resolve(child.exitCode);
  return new Promise((resolve, reject) => {
    let timeout = null;
    let settled = false;
    const cleanup = () => {
      child.removeListener('error', onError);
      child.removeListener('exit', onExit);
      if (timeout !== null) clearTimeout(timeout);
    };
    const settle = (callback, value) => {
      if (settled) return;
      settled = true;
      cleanup();
      callback(value);
    };
    const onError = error => settle(reject, error);
    const onExit = code => settle(resolve, code);
    child.once('error', onError);
    child.once('exit', onExit);
    if (Number.isFinite(timeoutMs) && timeoutMs > 0) {
      timeout = setTimeout(
        () => settle(reject, new Error(`${label} timed out after ${timeoutMs}ms`)),
        timeoutMs,
      );
    }
    if (child.exitCode !== null) onExit(child.exitCode);
  });
}

function waitForSupervisorSettlement(supervisor, timeoutMs, label) {
  const state = supervisorStates.get(supervisor);
  if (!state) return Promise.resolve(supervisor?.exitCode ?? null);
  if (state.closed) {
    return state.spawnError && !state.treeAbsenceProven
      ? Promise.reject(state.spawnError)
      : Promise.resolve(state.treeAbsenceProven ? 0 : state.exitCode);
  }
  const injectedWait = state.dependencies.waitForExit;
  const operation = injectedWait
    ? injectedWait(supervisor, timeoutMs, label)
    : state.exitPromise;
  return withTimeout(operation, timeoutMs, label);
}

async function waitForSupervisorExit(supervisor, timeoutMs, label) {
  const state = supervisorStates.get(supervisor);
  if (state?.protocolError) throw state.protocolError;
  const settlement = waitForSupervisorSettlement(supervisor, timeoutMs, label);
  const code = state
    ? await Promise.race([settlement, state.protocolFailurePromise])
    : await settlement;
  const failure = supervisorFailure(supervisor);
  if (failure) throw failure;
  return code;
}

function stopSupervisor(supervisor, dependencies = {}) {
  if (!supervisor) return Promise.resolve();
  const state = supervisorStates.get(supervisor);
  if (!state) return Promise.resolve();
  if (state.stopPromise) return state.stopPromise;
  const effectiveDependencies = {...state.dependencies, ...dependencies};
  const timeoutMs = processTreeTimeoutMs(effectiveDependencies);
  const now = monotonicNow(effectiveDependencies);
  const localDeadline = now() + timeoutMs;
  const deadline = Number.isFinite(effectiveDependencies.deadline)
    ? Math.min(localDeadline, effectiveDependencies.deadline)
    : localDeadline;
  state.stopPromise = (async () => {
    if (remaining(deadline, now) <= 0) throw stopDeadlineError();
    if (!state.exited && !state.spawnError && !state.stopWritten) {
      const writeTimeoutMs = Math.min(remaining(deadline, now), timeoutMs / 2);
      if (writeTimeoutMs <= 0) throw stopDeadlineError();
      state.stopWritten = true;
      const closeControlPipe = () => {
        try {
          if (!supervisor.stdin?.destroyed) supervisor.stdin?.destroy?.();
        } catch (_error) {
          // The original control failure remains authoritative.
        }
      };
      state.onControlError = error => {
        if (!state.controlError) state.controlError = error;
        const rejectWrite = state.controlWriteReject;
        state.controlWriteReject = null;
        if (rejectWrite) rejectWrite(error);
        closeControlPipe();
      };
      if (!state.controlGuardAttached && supervisor.stdin?.on) {
        state.controlGuardAttached = true;
        supervisor.stdin.on('error', state.onControlError);
      }
      const write = new Promise((resolve, reject) => {
        state.controlWriteReject = reject;
        if (!supervisor.stdin?.write) {
          const error = new Error('Supervisor control pipe is unavailable');
          error.code = 'EPIPE';
          state.onControlError(error);
          return;
        }
        try {
          supervisor.stdin.write('stop\n', error => {
            if (error) state.onControlError(error);
            else {
              state.controlWriteReject = null;
              resolve();
            }
          });
        } catch (error) {
          state.onControlError(error);
        }
      });
      try {
        await withTimeout(write, writeTimeoutMs, 'Supervisor stop request');
      } catch (error) {
        state.controlWriteReject = null;
        if (!state.controlError) state.controlError = error;
        closeControlPipe();
      }
    }
    try {
      const remainingForExit = remaining(deadline, now);
      if (remainingForExit <= 0) throw stopDeadlineError();
      const exitSettlement = waitForSupervisorSettlement(
        supervisor,
        remainingForExit,
        'Supervisor stop',
      );
      let observedProtocolFailure = null;
      await Promise.race([
        exitSettlement.then(() => undefined, () => undefined),
        state.protocolFailurePromise.catch(error => {
          observedProtocolFailure = error;
        }),
      ]);
      let exitFailure = null;
      try {
        const exitCode = await exitSettlement;
        if (exitCode !== 0) {
          exitFailure = new Error(`Supervisor exited with code ${exitCode}`);
        }
      } catch (error) {
        exitFailure = error;
      }
      let protocolFailure = observedProtocolFailure;
      try {
        if (state.protocolSettled) {
          await state.protocolSettlementPromise;
        } else {
          const remainingForProtocol = remaining(deadline, now);
          if (remainingForProtocol <= 0) throw stopDeadlineError();
          await withTimeout(
            state.protocolSettlementPromise,
            remainingForProtocol,
            'Supervisor readiness protocol settlement',
          );
        }
      } catch (error) {
        protocolFailure ||= error;
      }
      protocolFailure ||= state.protocolError;
      if (exitFailure && protocolFailure) {
        throw new AggregateError(
          [exitFailure, protocolFailure],
          'Supervisor exit and readiness protocol settlement failed',
          {cause: exitFailure},
        );
      }
      if (exitFailure) throw exitFailure;
      if (protocolFailure) throw protocolFailure;
    } catch (error) {
      if (state.controlError && error !== state.controlError) {
        throw new AggregateError(
          [state.controlError, error],
          'Supervisor control failed and close settlement also failed',
          {cause: state.controlError},
        );
      }
      throw error;
    }
    if (state.controlError) throw state.controlError;
  })();
  return state.stopPromise;
}

function cleanupGroup(children, runtimeRoot, stopChild = stopSupervisor) {
  const existing = runtimeCleanupPromises.get(runtimeRoot);
  if (existing) return existing;
  const operation = (async () => {
    const results = await Promise.allSettled(children.filter(Boolean).map(stopChild));
    const failures = Array.from(new Set(results
      .filter(result => result.status === 'rejected')
      .map(result => result.reason)));
    for (const child of children.filter(Boolean)) {
      const failure = supervisorStates.get(child)?.protocolError || null;
      if (failure && !failures.includes(failure)) failures.push(failure);
    }
    if (failures.length) {
      throw new AggregateError(failures, 'One or more test process supervisors did not stop');
    }
    fs.rmSync(runtimeRoot, {recursive: true, force: true});
    activeRuntimeRoots.delete(runtimeRoot);
  })();
  runtimeCleanupPromises.set(runtimeRoot, operation);
  operation.finally(() => {
    if (runtimeCleanupPromises.get(runtimeRoot) === operation) {
      runtimeCleanupPromises.delete(runtimeRoot);
    }
  }).catch(() => {});
  return operation;
}

function runnerState() {
  return {
    activeSupervisorCount: activeSupervisors.size,
    activeRunCount: activeRunOperations.size,
    activeRuntimeRoots: Array.from(activeRuntimeRoots),
  };
}

function waitForOperations(operations, timeoutMs, label) {
  if (!operations.length) return Promise.resolve([]);
  return withTimeout(Promise.allSettled(operations), timeoutMs, label);
}

function shutdown(signal, dependencies = {}) {
  if (shutdownPromise) return shutdownPromise;
  shuttingDown = true;
  const timeoutMs = Number.isFinite(dependencies.shutdownTimeoutMs)
    && dependencies.shutdownTimeoutMs > 0
    ? dependencies.shutdownTimeoutMs
    : DEFAULT_PROCESS_TREE_TIMEOUT_MS + 1000;
  const now = monotonicNow(dependencies);
  const deadline = now() + timeoutMs;
  const awaitOperations = dependencies.waitForOperations || waitForOperations;
  const exitProcess = dependencies.exitProcess || process.exit;
  shutdownPromise = (async () => {
    const supervisors = Array.from(activeSupervisors);
    const runs = Array.from(activeRunOperations);
    const cleanupFailures = [];
    const runFailures = [];
    try {
      const stopResults = await awaitOperations(
        supervisors.map(value => stopSupervisor(value, {
          ...dependencies,
          deadline,
          now,
        })),
        remaining(deadline, now),
        'Browser supervisor shutdown',
      );
      for (const failure of stopResults.filter(result => result.status === 'rejected')) {
        cleanupFailures.push(failure.reason);
      }
    } catch (error) {
      cleanupFailures.push(error);
    }
    try {
      const runResults = await awaitOperations(
        runs,
        remaining(deadline, now),
        'Browser run shutdown',
      );
      for (const failure of runResults.filter(result => result.status === 'rejected')) {
        runFailures.push(failure.reason);
      }
    } catch (error) {
      runFailures.push(error);
    } finally {
      const failures = flattenUniqueFailures([...runFailures, ...cleanupFailures]);
      for (const failure of failures) console.error(failure);
      const finalError = new AggregateError(failures, 'Browser runner shutdown did not converge');
      for (const supervisor of activeSupervisors) {
        supervisorStates.get(supervisor)?.prepareForExit(finalError);
      }
      const code = dependencies.exitCode
        ?? (signal === 'SIGINT' ? 130 : signal === 'SIGTERM' ? 143 : 1);
      exitProcess(code);
    }
  })();
  return shutdownPromise;
}

process.once('SIGINT', () => { void shutdown('SIGINT'); });
process.once('SIGTERM', () => { void shutdown('SIGTERM'); });

function runGroup(group, forwardedArgs, dependencies = {}) {
  if (shuttingDown) return Promise.reject(new Error('Browser runner shutdown is active'));
  const operation = Promise.resolve().then(
    () => _runGroup(group, forwardedArgs, dependencies),
  );
  activeRunOperations.add(operation);
  operation.then(
    () => activeRunOperations.delete(operation),
    () => activeRunOperations.delete(operation),
  );
  return operation;
}

async function _runGroup(group, forwardedArgs, dependencies = {}) {
  if (shuttingDown) throw new Error('Browser runner shutdown is active');
  const waitUntilHealthy = dependencies.waitForHealth || waitForHealth;
  const allocatePort = dependencies.freePort || freePort;
  const port = await allocatePort();
  if (shuttingDown) throw new Error('Browser runner shutdown started before server spawn');
  const baseURL = `http://127.0.0.1:${port}`;
  const healthToken = randomUUID();
  const runtimeRoot = path.join(
    os.tmpdir(),
    `morphic-browser-${process.pid}-${Date.now()}-${group || 'focus'}-${randomUUID()}`,
  );
  activeRuntimeRoots.add(runtimeRoot);
  const logs = {text: ''};
  const serverEnv = buildServerEnv(runtimeRoot, port, healthToken);
  let server = null;
  let tests = null;
  let primaryError = null;

  try {
    if (shuttingDown) throw new Error('Browser runner shutdown started before server spawn');
    const captureLog = chunk => {
      logs.text = `${logs.text}${chunk}`.slice(-20000);
    };
    server = spawnSupervised(
      resolvePython(),
      [SERVER_SCRIPT],
      {
        cwd: WORKTREE_ROOT,
        env: serverEnv,
        onStdout: captureLog,
        onStderr: captureLog,
        windowsHide: true,
      },
      dependencies,
    );
    await waitForSupervisorReady(server);
    await waitUntilHealthy(`${baseURL}/__browser-test-health`, healthToken, server, logs);
    const serverFailure = supervisorFailure(server);
    if (serverFailure) throw serverFailure;
    if (shuttingDown) throw new Error('Browser runner shutdown started before Playwright spawn');

    const args = [PLAYWRIGHT_CLI, 'test', '--config', 'playwright.config.js'];
    if (group) args.push('--fully-parallel', `--shard=${group}/${SHARD_COUNT}`);
    args.push(...forwardedArgs);
    const browser = resolveBrowser();
    tests = spawnSupervised(
      process.execPath,
      args,
      {
        cwd: BROWSER_DIR,
        env: buildTestEnv(baseURL, browser),
        stdout: 'inherit',
        stderr: 'inherit',
        windowsHide: true,
      },
      dependencies,
    );
    await waitForSupervisorReady(tests);
    const exitCode = await Promise.race([
      waitForSupervisorExit(
        tests,
        playwrightTimeoutMs(),
        `Playwright group ${group || 'focus'}`,
      ),
      supervisorStates.get(server).protocolFailurePromise,
    ]);
    if (exitCode !== 0) {
      throw new Error(`Playwright group ${group || 'focus'} failed with exit ${exitCode}`);
    }
  } catch (error) {
    primaryError = error;
    throw error;
  } finally {
    try {
      await cleanupGroup([tests, server], runtimeRoot);
    } catch (cleanupError) {
      throw combinePrimaryAndCleanup(primaryError, cleanupError);
    }
  }
}

async function main() {
  if (!fs.existsSync(PLAYWRIGHT_CLI)) {
    throw new Error('Playwright is not installed. Run: npm --prefix tests/browser ci');
  }
  const forwardedArgs = process.argv.slice(2);
  const groups = forwardedArgs.length ? [null] : [1, 2, 3, 4];
  for (const group of groups) await runGroup(group, forwardedArgs);
}

if (require.main === module) {
  main().catch(error => {
    console.error(error);
    if (!shuttingDown) void shutdown(null, {exitCode: 1});
  });
}

module.exports = {
  buildServerEnv,
  buildTestEnv,
  cleanupGroup,
  combinePrimaryAndCleanup,
  playwrightTimeoutMs,
  runGroup,
  runnerState,
  shutdown,
  spawnSupervised,
  stopSupervisor,
  trackSupervisor,
  waitForExit,
  waitForSupervisorExit,
  waitForSupervisorReady,
};
