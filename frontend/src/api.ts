import { Rubric } from './types';

const API_BASE_URL = 'http://localhost:5000'; // Assuming backend runs on port 5000

export const startEvaluation = async (data: {
  hackathonName: string;
  hackathonDescription: string;
  rubrics: Rubric[];
  additionalFiles: string[];
  ideasFile: string | null;
  ideasFileName: string;
}) => {
  try {
    const response = await fetch(`${API_BASE_URL}/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to start evaluation');
    }

    return await response.json();
  } catch (error) {
    console.error('Error starting evaluation:', error);
    throw error;
  }
};

export const getEvaluationProgress = async (evaluationId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/evaluation/progress/${evaluationId}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to get evaluation progress');
    }
    return await response.json();
  } catch (error) {
    console.error('Error getting evaluation progress:', error);
    throw error;
  }
};

export const getEvaluationResults = async (evaluationId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/evaluation/results/${evaluationId}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to get evaluation results');
    }
    return await response.json();
  } catch (error) {
    console.error('Error getting evaluation results:', error);
    throw error;
  }
};

export const generateRubricDescription = async (rubricName: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate-rubric-description`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ rubricName }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to generate rubric description');
    }

    const data = await response.json();
    return data.description;
  } catch (error) {
    console.error('Error generating rubric description:', error);
    throw error;
  }
};