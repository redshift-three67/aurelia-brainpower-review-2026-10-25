import Dexie, { Table } from 'dexie';
import { Patient, HarmonizationSession } from '@/types/patient';

export class AppDatabase extends Dexie {
  patients!: Table<Patient, string>;
  harmonizations!: Table<HarmonizationSession, string>;

  constructor() {
    super('CopenAppDatabase');
    
    this.version(1).stores({
      patients: 'id, firstName, lastName, birthDate, birthPlace, createdAt',
      harmonizations: 'id, patientId, word, status, completedAt, createdAt'
    });
  }
}

export const db = new AppDatabase();
