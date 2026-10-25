FROM python@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258
COPY wheels /wheels
COPY requirements-linux-c3a.lock /requirements-linux-c3a.lock
RUN python -m pip install --disable-pip-version-check --no-cache-dir --no-index --find-links=/wheels --require-hashes -r /requirements-linux-c3a.lock && python -m pip check && rm -r /wheels
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 65532:65532
