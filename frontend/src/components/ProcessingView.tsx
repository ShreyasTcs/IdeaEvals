import React, { useEffect, useState } from 'react';
import { Spinner, ProgressBar, Alert, Card } from 'react-bootstrap';
import { getEvaluationProgress } from '../api';

interface ProcessingViewProps {
  evaluationId: string;
  onEvaluationComplete: () => void;
}

const ProcessingView: React.FC<ProcessingViewProps> = ({ evaluationId, onEvaluationComplete }) => {
  const [progress, setProgress] = useState({
    total_ideas: 0,
    processed_ideas: 0,
    status: 'pending',
    estimated_time_remaining: 'N/A',
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const fetchProgress = async () => {
      try {
        const data = await getEvaluationProgress(evaluationId);
        setProgress(data);

        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(intervalId);
          onEvaluationComplete();
        }
      } catch (err) {
        console.error('Error fetching progress:', err);
        setError('Failed to fetch processing progress.');
        clearInterval(intervalId);
      }
    };

    intervalId = setInterval(fetchProgress, 3000); // Poll every 3 seconds
    fetchProgress(); // Fetch immediately on mount

    return () => clearInterval(intervalId);
  }, [evaluationId, onEvaluationComplete]);

  const percentage = progress.total_ideas > 0
    ? (progress.processed_ideas / progress.total_ideas) * 100
    : 0;

  return (
    <Card>
      <Card.Body>
        <Card.Title>Processing Evaluation</Card.Title>
        {error && <Alert variant="danger">{error}</Alert>}
        <div className="text-center my-4">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-3">Evaluation in progress...</p>
        </div>
        <ProgressBar now={percentage} label={`${percentage.toFixed(0)}%`} className="mb-3" />
        <p>Processed Ideas: {progress.processed_ideas} / {progress.total_ideas}</p>
        <p>Status: {progress.status}</p>
        <p>Estimated Time Remaining: {progress.estimated_time_remaining}</p>
      </Card.Body>
    </Card>
  );
};

export default ProcessingView;
