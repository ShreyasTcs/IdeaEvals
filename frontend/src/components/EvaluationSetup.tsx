import React, { useState, useMemo, useEffect } from 'react';
import { Form, Button, Card, Alert, Spinner } from 'react-bootstrap';
import FileUpload from './FileUpload';
import RubricEditor from './RubricEditor';
import ProcessingView from './ProcessingView';
import ResultsDashboard from './ResultsDashboard';
import { Rubric } from '../types';
import { startEvaluation } from '../api';

type ViewState = 'setup' | 'processing' | 'results';

interface EvaluationSetupProps {
  accessCode?: string;
  initialName?: string;
  initialDesc?: string;
  onEvaluationStarted?: () => void;
}

const EvaluationSetup: React.FC<EvaluationSetupProps> = ({ accessCode, initialName = '', initialDesc = '', onEvaluationStarted }) => {
  const [hackathonName, setHackathonName] = useState(initialName);
  const [hackathonDescription, setHackathonNameDescription] = useState(initialDesc);
  const [rubrics, setRubrics] = useState<Rubric[]>([]);
  const [additionalFiles, setAdditionalFiles] = useState<string[]>([]);
  const [ideasFile, setIdeasFile] = useState<File | null>(null);
  const [view, setView] = useState<ViewState>('setup');
  const [evaluationId, setEvaluationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (initialName) setHackathonName(initialName);
    if (initialDesc) setHackathonNameDescription(initialDesc);
  }, [initialName, initialDesc]);

  const totalWeight = useMemo(() => {
    return rubrics.reduce((sum, rubric) => sum + rubric.weight, 0);
  }, [rubrics]);

  const isWeightValid = totalWeight === 1;
  const canStartEvaluation = isWeightValid && rubrics.length > 0 && hackathonName.trim() !== '' && ideasFile !== null;

  const handleStartEvaluation = async () => {
    if (!canStartEvaluation) {
      alert('Please ensure hackathon name is entered, an ideas file is uploaded, rubric weights sum to 100%, and at least one rubric is defined.');
      return;
    }

    setIsLoading(true);
    let ideasFileBase64: string | null = null;

    if (ideasFile) {
      try {
        ideasFileBase64 = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.readAsDataURL(ideasFile);
          reader.onload = () => resolve(reader.result as string);
          reader.onerror = error => reject(error);
        });
      } catch (error) {
        alert('Failed to read ideas file.');
        console.error('Error reading ideas file:', error);
        setIsLoading(false);
        return;
      }
    }

    try {
      const response = await startEvaluation({
        hackathonName,
        hackathonDescription,
        rubrics,
        additionalFiles,
        ideasFile: ideasFileBase64, // Pass the base64 encoded file
        ideasFileName: ideasFile?.name || '',
        accessCode // Pass the access code if available
      });
      setEvaluationId(response.evaluationId);
      
      if (onEvaluationStarted) {
        onEvaluationStarted();
      } else {
        setView('processing'); // Fallback for legacy behavior if prop not passed
      }
    } catch (error) {
      alert('Failed to start evaluation. Please check console for details.');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderView = () => {
    switch (view) {
      case 'setup':
        return (
          <Card>
            <Card.Body>
              <Card.Title>Evaluation Setup {accessCode && <span className="text-muted fs-6">(Code: {accessCode})</span>}</Card.Title>
              <Form>
                <Form.Group className="mb-3" controlId="hackathonName">
                  <Form.Label>Hackathon Name</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Enter hackathon name"
                    value={hackathonName}
                    onChange={(e) => setHackathonName(e.target.value)}
                    required
                    disabled={!!accessCode} // Disable if linked
                  />
                </Form.Group>
                <Form.Group className="mb-3" controlId="hackathonDescription">
                  <Form.Label>Hackathon Description</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    placeholder="Enter hackathon description"
                    value={hackathonDescription}
                    onChange={(e) => setHackathonNameDescription(e.target.value)}
                    disabled={!!accessCode}
                  />
                </Form.Group>
              </Form>
              <hr />
              <RubricEditor onRubricsChange={setRubrics} />
              {rubrics.length > 0 && (
                <Alert variant={isWeightValid ? 'success' : 'danger'}>
                  Total Rubric Weight: {(totalWeight * 100).toFixed(0)}% {isWeightValid ? '(Valid)' : '(Must be 100%)'}
                </Alert>
              )}
              <hr />
              <FileUpload onAdditionalFilesChange={setAdditionalFiles} onIdeasFileChange={setIdeasFile} />
              <hr />
              <Button variant="primary" onClick={handleStartEvaluation} disabled={!canStartEvaluation || isLoading}>
                {isLoading ? <Spinner animation="border" size="sm" /> : 'Start Evaluation'}
              </Button>
            </Card.Body>
          </Card>
        );
      case 'processing':
        return evaluationId ? <ProcessingView evaluationId={evaluationId} onEvaluationComplete={() => setView('results')} /> : <Alert variant="danger">No evaluation ID found.</Alert>;
      case 'results':
        return evaluationId ? <ResultsDashboard evaluationId={evaluationId} /> : <Alert variant="danger">No evaluation ID found.</Alert>;
      default:
        return null;
    }
  };

  return <div className="evaluation-setup-container">{renderView()}</div>;
};

export default EvaluationSetup;
