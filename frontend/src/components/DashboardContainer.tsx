import React, { useEffect, useState } from 'react';
import { Spinner, Alert } from 'react-bootstrap';
import { getHackathonStatus } from '../api';
import ProcessingView from './ProcessingView';
import AdvancedDashboard from './AdvancedDashboard';

interface DashboardContainerProps {
  accessCode: string;
  onLogout: () => void;
}

const DashboardContainer: React.FC<DashboardContainerProps> = ({ accessCode, onLogout }) => {
  const [status, setStatus] = useState<'idle' | 'pending' | 'processing' | 'completed' | 'failed' | null>(null);
  const [evaluationId, setEvaluationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const data = await getHackathonStatus(accessCode);
        if (data.currentEvaluationId) {
          setEvaluationId(data.currentEvaluationId);
          setStatus(data.status);
        } else {
          setStatus('completed'); // Assume completed if no active ID (legacy/completed)
        }
      } catch (err: any) {
        setError('Failed to check status');
      } finally {
        setLoading(false);
      }
    };
    checkStatus();
  }, [accessCode]);

  if (loading) return <Spinner animation="border" className="d-block mx-auto mt-5" />;
  if (error) return <Alert variant="danger">{error}</Alert>;

  if ((status === 'processing' || status === 'pending') && evaluationId) {
    return (
      <ProcessingView 
        evaluationId={evaluationId} 
        onEvaluationComplete={() => setStatus('completed')} 
      />
    );
  }

  return <AdvancedDashboard accessCode={accessCode} onLogout={onLogout} />;
};

export default DashboardContainer;