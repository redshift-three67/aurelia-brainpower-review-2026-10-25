export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  public: {
    Tables: {
      analysis_archives: {
        Row: {
          analysis_timestamp: string
          copen_rate: string
          created_at: string
          database_entries: string[] | null
          highest_resonance_level: number | null
          highest_resonance_value: number | null
          id: string
          level_1_physical_particles: number | null
          level_10_causal_alchemy: number | null
          level_11_atmic_identity: number | null
          level_12_atmic_love: number | null
          level_13_creator: number | null
          level_2_physical_structure: number | null
          level_3_etheric_prana: number | null
          level_4_etheric_meridians: number | null
          level_5_astral_emotions: number | null
          level_6_astral_thoughts: number | null
          level_7_mental_time: number | null
          level_8_mental_constructs: number | null
          level_9_causal_blueprints: number | null
          patient_data: Json | null
          patient_id: string | null
          tested_potency: string | null
          updated_at: string
          user_id: string
          word: string
        }
        Insert: {
          analysis_timestamp?: string
          copen_rate: string
          created_at?: string
          database_entries?: string[] | null
          highest_resonance_level?: number | null
          highest_resonance_value?: number | null
          id?: string
          level_1_physical_particles?: number | null
          level_10_causal_alchemy?: number | null
          level_11_atmic_identity?: number | null
          level_12_atmic_love?: number | null
          level_13_creator?: number | null
          level_2_physical_structure?: number | null
          level_3_etheric_prana?: number | null
          level_4_etheric_meridians?: number | null
          level_5_astral_emotions?: number | null
          level_6_astral_thoughts?: number | null
          level_7_mental_time?: number | null
          level_8_mental_constructs?: number | null
          level_9_causal_blueprints?: number | null
          patient_data?: Json | null
          patient_id?: string | null
          tested_potency?: string | null
          updated_at?: string
          user_id: string
          word: string
        }
        Update: {
          analysis_timestamp?: string
          copen_rate?: string
          created_at?: string
          database_entries?: string[] | null
          highest_resonance_level?: number | null
          highest_resonance_value?: number | null
          id?: string
          level_1_physical_particles?: number | null
          level_10_causal_alchemy?: number | null
          level_11_atmic_identity?: number | null
          level_12_atmic_love?: number | null
          level_13_creator?: number | null
          level_2_physical_structure?: number | null
          level_3_etheric_prana?: number | null
          level_4_etheric_meridians?: number | null
          level_5_astral_emotions?: number | null
          level_6_astral_thoughts?: number | null
          level_7_mental_time?: number | null
          level_8_mental_constructs?: number | null
          level_9_causal_blueprints?: number | null
          patient_data?: Json | null
          patient_id?: string | null
          tested_potency?: string | null
          updated_at?: string
          user_id?: string
          word?: string
        }
        Relationships: []
      }
      analysis_archives_v2: {
        Row: {
          analysis_timestamp: string
          copen_rate: string
          created_at: string
          database_entries: string[] | null
          highest_resonance_level: number | null
          highest_resonance_value: number | null
          id: string
          level_1_physical_particles: number | null
          level_10_causal_alchemy: number | null
          level_11_atmic_identity: number | null
          level_12_atmic_love: number | null
          level_13_creator: number | null
          level_2_physical_structure: number | null
          level_3_etheric_prana: number | null
          level_4_etheric_meridians: number | null
          level_5_astral_emotions: number | null
          level_6_astral_thoughts: number | null
          level_7_mental_time: number | null
          level_8_mental_constructs: number | null
          level_9_causal_blueprints: number | null
          patient_data: Json | null
          patient_id: string | null
          tested_potency: string | null
          updated_at: string
          user_id: string
          word: string
        }
        Insert: {
          analysis_timestamp?: string
          copen_rate: string
          created_at?: string
          database_entries?: string[] | null
          highest_resonance_level?: number | null
          highest_resonance_value?: number | null
          id?: string
          level_1_physical_particles?: number | null
          level_10_causal_alchemy?: number | null
          level_11_atmic_identity?: number | null
          level_12_atmic_love?: number | null
          level_13_creator?: number | null
          level_2_physical_structure?: number | null
          level_3_etheric_prana?: number | null
          level_4_etheric_meridians?: number | null
          level_5_astral_emotions?: number | null
          level_6_astral_thoughts?: number | null
          level_7_mental_time?: number | null
          level_8_mental_constructs?: number | null
          level_9_causal_blueprints?: number | null
          patient_data?: Json | null
          patient_id?: string | null
          tested_potency?: string | null
          updated_at?: string
          user_id: string
          word: string
        }
        Update: {
          analysis_timestamp?: string
          copen_rate?: string
          created_at?: string
          database_entries?: string[] | null
          highest_resonance_level?: number | null
          highest_resonance_value?: number | null
          id?: string
          level_1_physical_particles?: number | null
          level_10_causal_alchemy?: number | null
          level_11_atmic_identity?: number | null
          level_12_atmic_love?: number | null
          level_13_creator?: number | null
          level_2_physical_structure?: number | null
          level_3_etheric_prana?: number | null
          level_4_etheric_meridians?: number | null
          level_5_astral_emotions?: number | null
          level_6_astral_thoughts?: number | null
          level_7_mental_time?: number | null
          level_8_mental_constructs?: number | null
          level_9_causal_blueprints?: number | null
          patient_data?: Json | null
          patient_id?: string | null
          tested_potency?: string | null
          updated_at?: string
          user_id?: string
          word?: string
        }
        Relationships: []
      }
      harmonization_sessions: {
        Row: {
          completed_at: string | null
          copen_rate: string | null
          created_at: string
          duration_seconds: number
          id: string
          job_last_heartbeat: string | null
          job_started_at: string | null
          patient_id: string
          progress: number | null
          remaining_seconds: number | null
          started_at: string | null
          status: string
          tested_potency: string | null
          updated_at: string
          user_id: string | null
          word: string
        }
        Insert: {
          completed_at?: string | null
          copen_rate?: string | null
          created_at?: string
          duration_seconds: number
          id?: string
          job_last_heartbeat?: string | null
          job_started_at?: string | null
          patient_id: string
          progress?: number | null
          remaining_seconds?: number | null
          started_at?: string | null
          status?: string
          tested_potency?: string | null
          updated_at?: string
          user_id?: string | null
          word: string
        }
        Update: {
          completed_at?: string | null
          copen_rate?: string | null
          created_at?: string
          duration_seconds?: number
          id?: string
          job_last_heartbeat?: string | null
          job_started_at?: string | null
          patient_id?: string
          progress?: number | null
          remaining_seconds?: number | null
          started_at?: string | null
          status?: string
          tested_potency?: string | null
          updated_at?: string
          user_id?: string | null
          word?: string
        }
        Relationships: [
          {
            foreignKeyName: "harmonization_sessions_patient_id_fkey"
            columns: ["patient_id"]
            isOneToOne: false
            referencedRelation: "patients"
            referencedColumns: ["id"]
          },
        ]
      }
      harmonization_sessions_v2: {
        Row: {
          batch_id: string | null
          completed_at: string | null
          copen_rate: string | null
          created_at: string
          duration_seconds: number
          id: string
          job_last_heartbeat: string | null
          job_started_at: string | null
          patient_id: string
          pause_seconds: number | null
          progress: number | null
          pulse_pause_active: boolean | null
          pulse_seconds: number | null
          remaining_seconds: number | null
          source_module: string | null
          started_at: string | null
          status: string
          tested_potency: string | null
          updated_at: string
          user_id: string | null
          word: string
        }
        Insert: {
          batch_id?: string | null
          completed_at?: string | null
          copen_rate?: string | null
          created_at?: string
          duration_seconds: number
          id?: string
          job_last_heartbeat?: string | null
          job_started_at?: string | null
          patient_id: string
          pause_seconds?: number | null
          progress?: number | null
          pulse_pause_active?: boolean | null
          pulse_seconds?: number | null
          remaining_seconds?: number | null
          source_module?: string | null
          started_at?: string | null
          status?: string
          tested_potency?: string | null
          updated_at?: string
          user_id?: string | null
          word: string
        }
        Update: {
          batch_id?: string | null
          completed_at?: string | null
          copen_rate?: string | null
          created_at?: string
          duration_seconds?: number
          id?: string
          job_last_heartbeat?: string | null
          job_started_at?: string | null
          patient_id?: string
          pause_seconds?: number | null
          progress?: number | null
          pulse_pause_active?: boolean | null
          pulse_seconds?: number | null
          remaining_seconds?: number | null
          source_module?: string | null
          started_at?: string | null
          status?: string
          tested_potency?: string | null
          updated_at?: string
          user_id?: string | null
          word?: string
        }
        Relationships: []
      }
      harmonization_templates: {
        Row: {
          created_at: string
          description: string | null
          id: string
          name: string
          patient_id: string
          sessions: Json
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          description?: string | null
          id?: string
          name: string
          patient_id: string
          sessions: Json
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          description?: string | null
          id?: string
          name?: string
          patient_id?: string
          sessions?: Json
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      harmonization_templates_v2: {
        Row: {
          created_at: string
          description: string | null
          id: string
          name: string
          patient_id: string
          sessions: Json
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          description?: string | null
          id?: string
          name: string
          patient_id: string
          sessions: Json
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          description?: string | null
          id?: string
          name?: string
          patient_id?: string
          sessions?: Json
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      morphic_field_calculations: {
        Row: {
          bohm_integration: Json | null
          client_name: string
          coherence: number
          created_at: string
          field_intensity: number
          geometric_form: string | null
          id: string
          intention_type: string | null
          numerical_sequence: Json | null
          patient_id: string | null
          quantum_states: Json | null
          recommendations: Json | null
          resonance_frequency: number
          tcm_analysis: Json | null
          user_id: string
        }
        Insert: {
          bohm_integration?: Json | null
          client_name: string
          coherence: number
          created_at?: string
          field_intensity: number
          geometric_form?: string | null
          id?: string
          intention_type?: string | null
          numerical_sequence?: Json | null
          patient_id?: string | null
          quantum_states?: Json | null
          recommendations?: Json | null
          resonance_frequency: number
          tcm_analysis?: Json | null
          user_id: string
        }
        Update: {
          bohm_integration?: Json | null
          client_name?: string
          coherence?: number
          created_at?: string
          field_intensity?: number
          geometric_form?: string | null
          id?: string
          intention_type?: string | null
          numerical_sequence?: Json | null
          patient_id?: string | null
          quantum_states?: Json | null
          recommendations?: Json | null
          resonance_frequency?: number
          tcm_analysis?: Json | null
          user_id?: string
        }
        Relationships: []
      }
      morphic_field_sessions: {
        Row: {
          batch_id: string | null
          coherence: number | null
          completed_at: string | null
          copen_rate: string | null
          created_at: string
          duration_seconds: number
          field_intensity: number | null
          geometric_form: string | null
          id: string
          intention_type: string | null
          job_last_heartbeat: string | null
          job_started_at: string | null
          patient_id: string
          pause_seconds: number | null
          progress: number | null
          pulse_pause_active: boolean | null
          pulse_seconds: number | null
          remaining_seconds: number | null
          started_at: string | null
          status: string
          tested_potency: string | null
          updated_at: string
          user_id: string
          word: string
        }
        Insert: {
          batch_id?: string | null
          coherence?: number | null
          completed_at?: string | null
          copen_rate?: string | null
          created_at?: string
          duration_seconds: number
          field_intensity?: number | null
          geometric_form?: string | null
          id?: string
          intention_type?: string | null
          job_last_heartbeat?: string | null
          job_started_at?: string | null
          patient_id: string
          pause_seconds?: number | null
          progress?: number | null
          pulse_pause_active?: boolean | null
          pulse_seconds?: number | null
          remaining_seconds?: number | null
          started_at?: string | null
          status?: string
          tested_potency?: string | null
          updated_at?: string
          user_id: string
          word: string
        }
        Update: {
          batch_id?: string | null
          coherence?: number | null
          completed_at?: string | null
          copen_rate?: string | null
          created_at?: string
          duration_seconds?: number
          field_intensity?: number | null
          geometric_form?: string | null
          id?: string
          intention_type?: string | null
          job_last_heartbeat?: string | null
          job_started_at?: string | null
          patient_id?: string
          pause_seconds?: number | null
          progress?: number | null
          pulse_pause_active?: boolean | null
          pulse_seconds?: number | null
          remaining_seconds?: number | null
          started_at?: string | null
          status?: string
          tested_potency?: string | null
          updated_at?: string
          user_id?: string
          word?: string
        }
        Relationships: []
      }
      patients: {
        Row: {
          birth_date: string
          birth_place: string
          created_at: string
          first_name: string
          id: string
          image_signature: string | null
          image_signature_active: boolean | null
          last_name: string
          updated_at: string
          user_id: string | null
        }
        Insert: {
          birth_date: string
          birth_place: string
          created_at?: string
          first_name: string
          id?: string
          image_signature?: string | null
          image_signature_active?: boolean | null
          last_name: string
          updated_at?: string
          user_id?: string | null
        }
        Update: {
          birth_date?: string
          birth_place?: string
          created_at?: string
          first_name?: string
          id?: string
          image_signature?: string | null
          image_signature_active?: boolean | null
          last_name?: string
          updated_at?: string
          user_id?: string | null
        }
        Relationships: []
      }
      patients_v2: {
        Row: {
          birth_date: string
          birth_place: string
          created_at: string
          first_name: string
          hardware_config: Json | null
          id: string
          image_signature: string | null
          image_signature_active: boolean | null
          last_name: string
          personal_rate: string | null
          updated_at: string
          user_id: string
        }
        Insert: {
          birth_date: string
          birth_place: string
          created_at?: string
          first_name: string
          hardware_config?: Json | null
          id?: string
          image_signature?: string | null
          image_signature_active?: boolean | null
          last_name: string
          personal_rate?: string | null
          updated_at?: string
          user_id: string
        }
        Update: {
          birth_date?: string
          birth_place?: string
          created_at?: string
          first_name?: string
          hardware_config?: Json | null
          id?: string
          image_signature?: string | null
          image_signature_active?: boolean | null
          last_name?: string
          personal_rate?: string | null
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      user_roles: {
        Row: {
          created_at: string
          id: string
          role: Database["public"]["Enums"]["app_role"]
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          role?: Database["public"]["Enums"]["app_role"]
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          role?: Database["public"]["Enums"]["app_role"]
          user_id?: string
        }
        Relationships: []
      }
      word_databases: {
        Row: {
          created_at: string
          entries: string[]
          id: string
          name: string
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          entries: string[]
          id?: string
          name: string
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          entries?: string[]
          id?: string
          name?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      word_energy_archives: {
        Row: {
          average_resonance: number | null
          client_name: string
          client_wellenfunktion: number | null
          created_at: string
          id: string
          patient_id: string
          results: Json
          top_items: Json | null
          total_words: number
          updated_at: string
          user_id: string
        }
        Insert: {
          average_resonance?: number | null
          client_name: string
          client_wellenfunktion?: number | null
          created_at?: string
          id?: string
          patient_id: string
          results: Json
          top_items?: Json | null
          total_words?: number
          updated_at?: string
          user_id: string
        }
        Update: {
          average_resonance?: number | null
          client_name?: string
          client_wellenfunktion?: number | null
          created_at?: string
          id?: string
          patient_id?: string
          results?: Json
          top_items?: Json | null
          total_words?: number
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      has_role: {
        Args: {
          _role: Database["public"]["Enums"]["app_role"]
          _user_id: string
        }
        Returns: boolean
      }
    }
    Enums: {
      app_role: "admin" | "user"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never) = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      app_role: ["admin", "user"],
    },
  },
} as const
