import { Rubric } from './types';

const API_BASE_URL = 'http://localhost:5000'; // Assuming backend runs on port 5000

// --- Hackathon Management ---

export const initHackathon = async (name: string, description: string, passkey: string) => {
  const response = await fetch(`${API_BASE_URL}/api/hackathon/init`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description, passkey }),
  });
  if (!response.ok) throw new Error('Failed to initialize hackathon');
  return await response.json(); // Returns { accessCode, hackathonId }
};

export const loginHackathon = async (accessCode: string, passkey: string) => {
  const response = await fetch(`${API_BASE_URL}/api/hackathon/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ accessCode, passkey }),
  });
  if (!response.ok) throw new Error('Invalid credentials');
  return await response.json(); // Returns { success: true }
};

export const getHackathonDashboard = async (accessCode: string) => {
  const response = await fetch(`${API_BASE_URL}/api/hackathon/${accessCode}/dashboard`);
  if (!response.ok) throw new Error('Failed to fetch dashboard');
  return await response.json();
};

export const getHackathonStatus = async (accessCode: string) => {
  const response = await fetch(`${API_BASE_URL}/api/hackathon/${accessCode}/status`);
  if (!response.ok) throw new Error('Failed to fetch status');
  return await response.json();
};

export const getIdeaDetails = async (ideaId: string) => {
  const response = await fetch(`${API_BASE_URL}/api/idea/${ideaId}/details`);
  if (!response.ok) throw new Error('Failed to fetch idea details');
  return await response.json();
};

// --- Evaluation ---

export const startEvaluation = async (data: {
  hackathonName: string;
  hackathonDescription: string;
  rubrics: Rubric[];
  additionalFiles: string[];
  ideasFile: string | null;
  ideasFileName: string;
  accessCode?: string; // Added
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