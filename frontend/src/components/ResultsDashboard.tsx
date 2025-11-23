import React, { useEffect, useState, useMemo } from 'react';
import { Card, Alert, Spinner, Table } from 'react-bootstrap';
import { getEvaluationResults } from '../api';

interface ResultsDashboardProps {
  evaluationId: string;
}

interface RawIdeaData {
  idea_id: string;
  idea_title?: string;
  brief_summary?: string;
  llm_output?: {
    evaluation?: {
      weighted_total: number;
      rubric_weights: { [key: string]: number };
      [key: string]: any; // For other evaluation details
    };
    [key: string]: any; // For other llm_output details
  };
  [key: string]: any; // For other top-level idea details
}

interface ProcessedIdeaResult {
  idea_id: string;
  idea_title: string;
  overall_score: number;
  rubric_scores: { [key: string]: { score: number; reasoning: string } };
  summary: string;
  // Add other fields you want to display directly
}

const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ evaluationId }) => {
  const [results, setResults] = useState<ProcessedIdeaResult[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setIsLoading(true);
        const rawData: RawIdeaData[] = await getEvaluationResults(evaluationId);

        const processedResults: ProcessedIdeaResult[] = rawData.map(item => ({
          idea_id: item.idea_id,
          idea_title: item.idea_title || 'N/A',
          overall_score: item.llm_output?.evaluation?.weighted_total || 0,
          rubric_scores: item.llm_output?.evaluation?.criteria || {}, // Assuming rubric scores are under 'criteria'
          summary: item.llm_output?.evaluation?.summary || item.brief_summary || 'N/A',
        }));
        setResults(processedResults);
      } catch (err) {
        console.error('Error fetching results:', err);
        setError('Failed to load evaluation results.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [evaluationId]);

  const sortedIdeas = useMemo(() => {
    if (!results) return [];
    return [...results].sort((a, b) => b.overall_score - a.overall_score);
  }, [results]);

  const overallAverageScore = useMemo(() => {
    if (!results || results.length === 0) return 0;
    const totalScore = results.reduce((sum, idea) => sum + idea.overall_score, 0);
    return totalScore / results.length;
  }, [results]);

  if (isLoading) {
    return (
      <Card>
        <Card.Body>
          <Card.Title>Loading Results...</Card.Title>
          <div className="text-center my-4">
            <Spinner animation="border" role="status" />
          </div>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <Card.Body>
          <Card.Title>Evaluation Results</Card.Title>
          <Alert variant="danger">{error}</Alert>
        </Card.Body>
      </Card>
    );
  }

  if (!results || results.length === 0) {
    return (
      <Card>
        <Card.Body>
          <Card.Title>Evaluation Results</Card.Title>
          <Alert variant="info">No results available for this evaluation ID.</Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card>
      <Card.Body>
        <Card.Title>Evaluation Results</Card.Title>
        <h4 className="mt-4">Overall Statistics</h4>
        <p>Total Ideas Evaluated: {results.length}</p>
        <p>Average Overall Score: {overallAverageScore.toFixed(2)}</p>

        <h4 className="mt-4">Top 10 Ideas</h4>
        <Table striped bordered hover responsive className="mt-3">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Idea Title</th>
              <th>Overall Score</th>
              {/* Add more headers for rubric scores if desired */}
            </tr>
          </thead>
          <tbody>
            {sortedIdeas.slice(0, 10).map((idea, index) => (
              <tr key={idea.idea_id}>
                <td>{index + 1}</td>
                <td>{idea.idea_title || 'N/A'}</td>
                <td>{idea.overall_score.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </Table>

        <h4 className="mt-4">All Results (Raw JSON for now)</h4>
        <pre style={{ maxHeight: '400px', overflowY: 'scroll', backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '5px' }}>
          {JSON.stringify(results, null, 2)}
        </pre>
      </Card.Body>
    </Card>
  );
};

export default ResultsDashboard;
