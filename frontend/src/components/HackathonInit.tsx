import React, { useState } from 'react';
import { Form, Button, Card, Alert, Container } from 'react-bootstrap';
import { initHackathon } from '../api';
import EvaluationSetup from './EvaluationSetup';

interface HackathonInitProps {
  onBack: () => void;
}

const HackathonInit: React.FC<HackathonInitProps> = ({ onBack }) => {
  const [step, setStep] = useState<'details' | 'setup'>('details');
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [passkey, setPasskey] = useState('');
  const [accessCode, setAccessCode] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleInit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await initHackathon(name, desc, passkey);
      setAccessCode(data.accessCode);
      setStep('setup');
    } catch (err: any) {
      setError(err.message || 'Initialization failed');
    } finally {
      setLoading(false);
    }
  };

  if (step === 'setup' && accessCode) {
    return (
      <Container>
        <Alert variant="success" className="mb-4">
          <Alert.Heading>Event Created Successfully!</Alert.Heading>
          <p>Your Access Code is: <strong>{accessCode}</strong></p>
          <p className="mb-0">Save this code and your passkey to access the results dashboard later.</p>
        </Alert>
        <EvaluationSetup 
          accessCode={accessCode} 
          initialName={name} 
          initialDesc={desc} 
          onEvaluationStarted={() => {
            alert('Process Started! Redirecting to Home...');
            onBack();
          }}
        />
      </Container>
    );
  }

  return (
    <div className="d-flex justify-content-center">
      <Card style={{ width: '500px' }} className="p-4 shadow-sm">
        <Card.Title className="text-center mb-4">Create New Event</Card.Title>
        {error && <Alert variant="danger">{error}</Alert>}
        <Form onSubmit={handleInit}>
          <Form.Group className="mb-3">
            <Form.Label>Event Name</Form.Label>
            <Form.Control 
              type="text" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              required 
              placeholder="e.g. AI Innovation 2025"
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control 
              as="textarea" 
              rows={2}
              value={desc} 
              onChange={(e) => setDesc(e.target.value)} 
            />
          </Form.Group>
          <Form.Group className="mb-4">
            <Form.Label>Set Passkey (for Dashboard Access)</Form.Label>
            <Form.Control 
              type="password" 
              value={passkey} 
              onChange={(e) => setPasskey(e.target.value)} 
              placeholder="Secure password"
            />
            <Form.Text className="text-muted">
              You will need this passkey + the generated access code to view results.
            </Form.Text>
          </Form.Group>
          <div className="d-grid gap-2">
            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create & Continue'}
            </Button>
            <Button variant="secondary" onClick={onBack}>
              Back
            </Button>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default HackathonInit;