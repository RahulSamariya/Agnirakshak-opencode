/** Zod validation schemas for the Heatwave Platform. */
import { z } from 'zod';

export const riskCategorySchema = z.enum(['low', 'medium', 'high']);

export const alertLevelSchema = z.enum(['info', 'warning', 'critical', 'emergency']);

export const stateSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  code: z.string(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const citySchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  state_id: z.string().uuid(),
  population: z.number().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const wardSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  city_id: z.string().uuid(),
  ward_code: z.string().nullable(),
  population: z.number().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const riskAssessmentSchema = z.object({
  id: z.string().uuid(),
  risk_run_id: z.string().uuid(),
  grid_cell_id: z.string().uuid(),
  valid_time: z.string().datetime(),
  hazard: z.number().min(0).max(1),
  vulnerability: z.number().min(0).max(1),
  exposure: z.number().min(0).max(1),
  hsri: z.number().min(0).max(1),
  risk_category: riskCategorySchema,
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const alertSchema = z.object({
  id: z.string().uuid(),
  alert_level: alertLevelSchema,
  alert_type: z.string(),
  title: z.string(),
  message: z.string(),
  valid_from: z.string().datetime(),
  valid_until: z.string().datetime(),
  issued_at: z.string().datetime(),
  is_active: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});
