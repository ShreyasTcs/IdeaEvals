import React, { useState } from 'react';
import { Form, Button, Card, Alert } from 'react-bootstrap';
import { loginHackathon } from '../api';

interface HackathonLoginProps {
  onLoginSuccess: (accessCode: string) => void;
  onBack: () => void;
}

const HackathonLogin: React.FC<HackathonLoginProps> = ({ onLoginSuccess, onBack }) => {
  const [accessCode, setAccessCode] = useState('');
  const [passkey, setPasskey] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await loginHackathon(accessCode, passkey);
      onLoginSuccess(accessCode);
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="d-flex justify-content-center">
      <Card style={{ width: '400px' }} className="p-4 shadow-sm">
        <Card.Title className="text-center mb-4">Access Event</Card.Title>
        {error && <Alert variant="danger">{error}</Alert>}
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Access Code</Form.Label>
            <Form.Control 
              type="text" 
              value={accessCode} 
              onChange={(e) => setAccessCode(e.target.value)} 
              required 
              placeholder="e.g. a1b2c3d4"
            />
          </Form.Group>
          <Form.Group className="mb-4">
            <Form.Label>Passkey</Form.Label>
            <Form.Control 
              type="password" 
              value={passkey} 
              onChange={(e) => setPasskey(e.target.value)} 
              required 
            />
          </Form.Group>
          <div className="d-grid gap-2">
            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? 'Verifying...' : 'Login'}
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

export default HackathonLogin;