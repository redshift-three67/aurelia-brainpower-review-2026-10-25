-- Add hardware_config column to patients_v2 table
ALTER TABLE patients_v2 
ADD COLUMN hardware_config JSONB DEFAULT NULL;

-- Add comment to explain the structure
COMMENT ON COLUMN patients_v2.hardware_config IS 'Patient-specific hardware algorithm configuration with rateGenerator and analysis settings';

-- Create index for faster queries on hardware_config
CREATE INDEX idx_patients_v2_hardware_config ON patients_v2 USING GIN (hardware_config);