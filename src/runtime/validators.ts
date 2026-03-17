import { ParameterDef, SkillExecution, Skill } from '../types';

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export class InputValidator {
  validate(inputs: Record<string, unknown>, schema: Record<string, ParameterDef>): ValidationResult {
    const errors: string[] = [];
    for (const [key, def] of Object.entries(schema)) {
      if (def.required && (inputs[key] === undefined || inputs[key] === null)) {
        errors.push(`Missing required input: ${key}`);
      } else if (inputs[key] !== undefined && inputs[key] !== null) {
        const actualType = Array.isArray(inputs[key]) ? 'array' : typeof inputs[key];
        if (actualType !== def.type) {
          errors.push(`Input ${key}: expected ${def.type}, got ${actualType}`);
        }
      }
    }
    return { valid: errors.length === 0, errors };
  }
}

export class OutputValidator {
  validate(outputs: Record<string, unknown>, schema: Record<string, ParameterDef>): ValidationResult {
    const errors: string[] = [];
    for (const [key, def] of Object.entries(schema)) {
      if (def.required && (outputs[key] === undefined || outputs[key] === null)) {
        errors.push(`Missing required output: ${key}`);
      } else if (outputs[key] !== undefined && outputs[key] !== null) {
        const actualType = Array.isArray(outputs[key]) ? 'array' : typeof outputs[key];
        if (actualType !== def.type) {
          errors.push(`Output ${key}: expected ${def.type}, got ${actualType}`);
        }
      }
    }
    return { valid: errors.length === 0, errors };
  }
}

export function validateExecution(execution: SkillExecution, skill: Skill): ValidationResult {
  const validator = new InputValidator();
  return validator.validate(execution.inputs, skill.inputs);
}
