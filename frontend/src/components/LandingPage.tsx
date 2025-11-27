import React from 'react';
import { Card, Button, Row, Col } from 'react-bootstrap';

interface LandingPageProps {
  onStartNew: () => void;
  onViewResults: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onStartNew, onViewResults }) => {
  return (
    <div className="landing-page">
      <h1 className="text-center mb-5">AI Hackathon Evaluator</h1>
      <Row className="justify-content-center">
        <Col md={5} className="mb-4">
          <Card className="h-100 text-center p-4 shadow-sm hover-card">
            <Card.Body>
              <Card.Title>Start New Evaluation</Card.Title>
              <Card.Text>
                Create a new hackathon event, upload ideas and rubrics, and let AI evaluate them.
              </Card.Text>
              <Button variant="primary" size="lg" onClick={onStartNew}>Create Event</Button>
            </Card.Body>
          </Card>
        </Col>
        <Col md={5} className="mb-4">
          <Card className="h-100 text-center p-4 shadow-sm hover-card">
            <Card.Body>
              <Card.Title>View Results</Card.Title>
              <Card.Text>
                Access the dashboard for an existing event using your Access Code and Passkey.
              </Card.Text>
              <Button variant="outline-primary" size="lg" onClick={onViewResults}>Login & View</Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default LandingPage;