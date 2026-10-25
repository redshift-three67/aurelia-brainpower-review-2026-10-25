/**
 * Harmonization Job Service
 * Verwaltet Hintergrund-Jobs für Harmonisierungs-Prozesse
 */
import { supabase } from '@/integrations/supabase/client';

export interface HarmonizationJob {
  id: string;
  clientId: string;
  vectorId: string | null;
  protocolId: string | null;
  jobType: 'harmonization' | 'analysis' | 'resonance_scan';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  priority: number;
  targetFrequencies: number[];
  targetAnatomyPoints: string[];
  targetWordEnergies: string[];
  progress: number;
  resultData: Record<string, unknown> | null;
  errorMessage: string | null;
  startedAt: Date | null;
  completedAt: Date | null;
  createdAt: Date;
}

export interface CreateJobParams {
  clientId: string;
  vectorId?: string;
  protocolId?: string;
  sessionId?: string;
  jobType?: 'harmonization' | 'analysis' | 'resonance_scan';
  priority?: number;
  targetFrequencies?: number[];
  targetAnatomyPoints?: string[];
  targetWordEnergies?: string[];
}

export interface BatchJobResult {
  total: number;
  completed: number;
  failed: number;
  jobs: HarmonizationJob[];
}

export interface JobUpdateParams {
  status?: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress?: number;
  resultData?: Record<string, unknown>;
  errorMessage?: string;
}

class HarmonizationJobServiceClass {
  private activeJobs: Map<string, HarmonizationJob> = new Map();
  private jobListeners: Map<string, Set<(job: HarmonizationJob) => void>> = new Map();
  private pollingIntervals: Map<string, ReturnType<typeof setInterval>> = new Map();

  /**
   * Neuen Job erstellen
   */
  async createJob(params: CreateJobParams): Promise<HarmonizationJob | null> {
    try {
      const { data, error } = await supabase
        .from('harmonization_jobs')
        .insert({
          client_id: params.clientId,
          vector_id: params.vectorId || null,
          protocol_id: params.protocolId || null,
          job_type: params.jobType || 'harmonization',
          priority: params.priority || 1,
          target_frequencies: params.targetFrequencies || [],
          target_anatomy_points: params.targetAnatomyPoints || [],
          target_word_energies: params.targetWordEnergies || [],
          status: 'pending',
          progress: 0,
        })
        .select()
        .single();

      if (error) throw error;

      const job = this.mapDbToJob(data);
      this.activeJobs.set(job.id, job);
      
      return job;
    } catch (error) {
      console.error('Error creating job:', error);
      return null;
    }
  }

  /**
   * Job starten
   */
  async startJob(jobId: string): Promise<boolean> {
    try {
      const { data, error } = await supabase
        .from('harmonization_jobs')
        .update({
          status: 'running',
          started_at: new Date().toISOString(),
        })
        .eq('id', jobId)
        .select()
        .single();

      if (error) throw error;

      const job = this.mapDbToJob(data);
      this.activeJobs.set(job.id, job);
      this.notifyListeners(job.id, job);

      // Start polling for this job
      this.startPolling(jobId);

      return true;
    } catch (error) {
      console.error('Error starting job:', error);
      return false;
    }
  }

  /**
   * Job aktualisieren
   */
  async updateJob(jobId: string, updates: JobUpdateParams): Promise<HarmonizationJob | null> {
    try {
      const updateData: Record<string, unknown> = {};
      
      if (updates.status) updateData.status = updates.status;
      if (updates.progress !== undefined) updateData.progress = updates.progress;
      if (updates.resultData) updateData.result_data = updates.resultData;
      if (updates.errorMessage) updateData.error_message = updates.errorMessage;

      if (updates.status === 'completed' || updates.status === 'failed') {
        updateData.completed_at = new Date().toISOString();
        this.stopPolling(jobId);
      }

      const { data, error } = await supabase
        .from('harmonization_jobs')
        .update(updateData)
        .eq('id', jobId)
        .select()
        .single();

      if (error) throw error;

      const job = this.mapDbToJob(data);
      this.activeJobs.set(job.id, job);
      this.notifyListeners(job.id, job);

      return job;
    } catch (error) {
      console.error('Error updating job:', error);
      return null;
    }
  }

  /**
   * Jobs für Client laden
   */
  async loadClientJobs(clientId: string): Promise<HarmonizationJob[]> {
    try {
      const { data, error } = await supabase
        .from('harmonization_jobs')
        .select('*')
        .eq('client_id', clientId)
        .order('created_at', { ascending: false })
        .limit(20);

      if (error) throw error;

      return (data || []).map(this.mapDbToJob);
    } catch (error) {
      console.error('Error loading jobs:', error);
      return [];
    }
  }

  /**
   * Pending Jobs laden (für Worker)
   */
  async loadPendingJobs(limit: number = 10): Promise<HarmonizationJob[]> {
    try {
      const { data, error } = await supabase
        .from('harmonization_jobs')
        .select('*')
        .eq('status', 'pending')
        .order('priority', { ascending: false })
        .order('created_at', { ascending: true })
        .limit(limit);

      if (error) throw error;

      return (data || []).map(this.mapDbToJob);
    } catch (error) {
      console.error('Error loading pending jobs:', error);
      return [];
    }
  }

  /**
   * Job-Listener hinzufügen
   */
  addJobListener(jobId: string, callback: (job: HarmonizationJob) => void): void {
    if (!this.jobListeners.has(jobId)) {
      this.jobListeners.set(jobId, new Set());
    }
    this.jobListeners.get(jobId)!.add(callback);
  }

  /**
   * Job-Listener entfernen
   */
  removeJobListener(jobId: string, callback: (job: HarmonizationJob) => void): void {
    const listeners = this.jobListeners.get(jobId);
    if (listeners) {
      listeners.delete(callback);
      if (listeners.size === 0) {
        this.jobListeners.delete(jobId);
      }
    }
  }

  /**
   * Simulierter Harmonisierungs-Prozess (für Demo)
   */
  async simulateHarmonization(jobId: string): Promise<void> {
    await this.startJob(jobId);

    // Simuliere Fortschritt
    const progressSteps = [10, 25, 40, 55, 70, 85, 95, 100];
    
    for (const progress of progressSteps) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (progress < 100) {
        await this.updateJob(jobId, { progress });
      } else {
        await this.updateJob(jobId, {
          status: 'completed',
          progress: 100,
          resultData: {
            harmonizationScore: 0.85,
            frequenciesApplied: 5,
            duration: progressSteps.length,
            resonanceImprovement: 0.23,
            stabilityGain: 0.18,
          }
        });
      }
    }
  }

  /**
   * Batch-Jobs erstellen und sequenziell ausführen
   */
  async createBatchJobs(params: CreateJobParams[]): Promise<BatchJobResult> {
    const result: BatchJobResult = { total: params.length, completed: 0, failed: 0, jobs: [] };
    
    for (const p of params) {
      const job = await this.createJob(p);
      if (job) {
        result.jobs.push(job);
      } else {
        result.failed++;
      }
    }
    
    return result;
  }

  /**
   * Job abbrechen
   */
  async cancelJob(jobId: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('harmonization_jobs')
        .update({ status: 'cancelled', completed_at: new Date().toISOString() })
        .eq('id', jobId);

      if (error) throw error;
      this.stopPolling(jobId);
      this.activeJobs.delete(jobId);
      return true;
    } catch (error) {
      console.error('Error cancelling job:', error);
      return false;
    }
  }

  /**
   * Alle aktiven Jobs beenden
   */
  cleanup(): void {
    this.pollingIntervals.forEach((interval) => clearInterval(interval));
    this.pollingIntervals.clear();
    this.jobListeners.clear();
    this.activeJobs.clear();
  }

  // Private Methoden
  private mapDbToJob(data: Record<string, unknown>): HarmonizationJob {
    return {
      id: data.id as string,
      clientId: data.client_id as string,
      vectorId: data.vector_id as string | null,
      protocolId: data.protocol_id as string | null,
      jobType: data.job_type as 'harmonization' | 'analysis' | 'resonance_scan',
      status: data.status as 'pending' | 'running' | 'completed' | 'failed' | 'cancelled',
      priority: data.priority as number,
      targetFrequencies: (data.target_frequencies as number[]) || [],
      targetAnatomyPoints: (data.target_anatomy_points as string[]) || [],
      targetWordEnergies: (data.target_word_energies as string[]) || [],
      progress: data.progress as number,
      resultData: data.result_data as Record<string, unknown> | null,
      errorMessage: data.error_message as string | null,
      startedAt: data.started_at ? new Date(data.started_at as string) : null,
      completedAt: data.completed_at ? new Date(data.completed_at as string) : null,
      createdAt: new Date(data.created_at as string),
    };
  }

  private notifyListeners(jobId: string, job: HarmonizationJob): void {
    const listeners = this.jobListeners.get(jobId);
    if (listeners) {
      listeners.forEach(callback => callback(job));
    }
  }

  private startPolling(jobId: string): void {
    if (this.pollingIntervals.has(jobId)) return;

    const interval = setInterval(async () => {
      try {
        const { data, error } = await supabase
          .from('harmonization_jobs')
          .select('*')
          .eq('id', jobId)
          .single();

        if (error) throw error;

        const job = this.mapDbToJob(data);
        this.activeJobs.set(job.id, job);
        this.notifyListeners(job.id, job);

        // Stop polling wenn Job abgeschlossen
        if (job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled') {
          this.stopPolling(jobId);
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 2000);

    this.pollingIntervals.set(jobId, interval);
  }

  private stopPolling(jobId: string): void {
    const interval = this.pollingIntervals.get(jobId);
    if (interval) {
      clearInterval(interval);
      this.pollingIntervals.delete(jobId);
    }
  }
}

export const HarmonizationJobService = new HarmonizationJobServiceClass();
export default HarmonizationJobService;
