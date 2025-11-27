import React, { useEffect, useState, useMemo } from 'react';
import { Card, Alert, Spinner, Table, Form, Row, Col, Button, Modal, Badge } from 'react-bootstrap';
import { getHackathonDashboard, getIdeaDetails } from '../api';

interface AdvancedDashboardProps {
  accessCode: string;
  onLogout: () => void;
}

interface IdeaSummary {
  idea_id: string;
  title: string;
  summary: string;
  theme: string;
  industry: string;
  status: string;
  total_score: number;
}

interface IdeaDetailData {
  [key: string]: any;
}

const AdvancedDashboard: React.FC<AdvancedDashboardProps> = ({ accessCode, onLogout }) => {
  const [ideas, setIdeas] = useState<IdeaSummary[]>([]);
  const [hackathonName, setHackathonName] = useState('Hackathon');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Search
  const [searchTerm, setSearchTerm] = useState('');
  const [themeFilter, setThemeFilter] = useState('');
  const [sortField, setSortField] = useState<'total_score' | 'title'>('total_score');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  // Modal
  const [selectedIdea, setSelectedIdea] = useState<string | null>(null);
  const [detailData, setDetailData] = useState<IdeaDetailData | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await getHackathonDashboard(accessCode);
        setHackathonName(data.hackathon_name);
        setIdeas(data.ideas);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [accessCode]);

  const handleShowDetails = async (ideaId: string) => {
    setSelectedIdea(ideaId);
    setLoadingDetail(true);
    try {
      const data = await getIdeaDetails(ideaId);
      setDetailData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDetail(false);
    }
  };

  const filteredIdeas = useMemo(() => {
    return ideas.filter(idea => {
      const matchesSearch = 
        idea.title?.toLowerCase().includes(searchTerm.toLowerCase()) || 
        idea.idea_id?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesTheme = themeFilter ? idea.theme === themeFilter : true;
      return matchesSearch && matchesTheme;
    }).sort((a, b) => {
      const valA = a[sortField];
      const valB = b[sortField];
      if (valA < valB) return sortDir === 'asc' ? -1 : 1;
      if (valA > valB) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [ideas, searchTerm, themeFilter, sortField, sortDir]);

  // Stats
  const stats = useMemo(() => {
    const total = ideas.length;
    const avgScore = total > 0 ? ideas.reduce((acc, i) => acc + i.total_score, 0) / total : 0;
    const themes = ideas.reduce((acc, i) => {
      acc[i.theme] = (acc[i.theme] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    const topTheme = Object.entries(themes).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';
    
    return { total, avgScore, topTheme };
  }, [ideas]);

  if (loading) return <Spinner animation="border" className="d-block mx-auto mt-5" />;
  if (error) return <Alert variant="danger">{error}</Alert>;

  return (
    <div className="advanced-dashboard">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{hackathonName} Dashboard <span className="text-muted fs-6">(Code: {accessCode})</span></h2>
        <Button variant="outline-danger" onClick={onLogout}>Logout</Button>
      </div>

      {/* Stats Cards */}
      <Row className="mb-4 text-center">
        <Col md={4}>
          <Card className="bg-light">
            <Card.Body>
              <h3>{stats.total}</h3>
              <span className="text-muted">Total Ideas</span>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="bg-light">
            <Card.Body>
              <h3>{stats.avgScore.toFixed(1)}</h3>
              <span className="text-muted">Avg. Score</span>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="bg-light">
            <Card.Body>
              <h3 className="text-truncate">{stats.topTheme}</h3>
              <span className="text-muted">Top Theme</span>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Filters */}
      <Card className="mb-4 p-3">
        <Row>
          <Col md={4}>
            <Form.Control 
              placeholder="Search by Title or ID..." 
              value={searchTerm} 
              onChange={(e) => setSearchTerm(e.target.value)} 
            />
          </Col>
          <Col md={3}>
            <Form.Select value={themeFilter} onChange={(e) => setThemeFilter(e.target.value)}>
              <option value="">All Themes</option>
              {ideas
                .map(i => i.theme)
                .filter(Boolean)
                .filter((t, index, self) => self.indexOf(t) === index)
                .map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
            </Form.Select>
          </Col>
          <Col md={3}>
            <Form.Select value={`${sortField}-${sortDir}`} onChange={(e) => {
              const [field, dir] = e.target.value.split('-');
              setSortField(field as any);
              setSortDir(dir as any);
            }}>
              <option value="total_score-desc">Score (High-Low)</option>
              <option value="total_score-asc">Score (Low-High)</option>
              <option value="title-asc">Title (A-Z)</option>
            </Form.Select>
          </Col>
        </Row>
      </Card>

      {/* Table */}
      <Table hover responsive striped>
        <thead className="bg-dark text-white">
          <tr>
            <th>Score</th>
            <th>Title</th>
            <th>ID</th>
            <th>Theme</th>
            <th>Industry</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {filteredIdeas.map(idea => (
            <tr key={idea.idea_id}>
              <td><strong>{idea.total_score.toFixed(1)}</strong></td>
              <td>{idea.title}</td>
              <td>{idea.idea_id}</td>
              <td>{idea.theme}</td>
              <td>{idea.industry}</td>
              <td>
                <Badge bg={idea.status === 'failed' ? 'danger' : 'success'}>
                  {idea.status || 'Completed'}
                </Badge>
              </td>
              <td>
                <Button size="sm" variant="info" onClick={() => handleShowDetails(idea.idea_id)}>View</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      {/* Detail Modal */}
      <Modal show={!!selectedIdea} onHide={() => setSelectedIdea(null)} size="xl">
        <Modal.Header closeButton>
          <Modal.Title>Idea Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {loadingDetail ? <Spinner animation="border" /> : detailData ? (
            <div>
              <h4>{detailData.idea_title}</h4>
              <p className="lead">{detailData.brief_summary}</p>
              <hr />
              
              <h5>Evaluation</h5>
              <Row>
                {Object.entries(detailData.llm_output?.evaluation || {}).map(([key, val]: any) => {
                  if (['weighted_total', 'rubric_weights', 'schema_version'].includes(key)) return null;
                  return (
                    <Col md={6} key={key} className="mb-3">
                      <Card>
                        <Card.Header className="text-capitalize">
                          {key.replace(/_/g, ' ')} 
                          {val.score && <Badge bg="primary" className="float-end">{val.score}</Badge>}
                        </Card.Header>
                        <Card.Body>
                          <Card.Text>{val.reasoning || val.justification || JSON.stringify(val)}</Card.Text>
                        </Card.Body>
                      </Card>
                    </Col>
                  )
                })}
              </Row>

              <h5 className="mt-4">Classification</h5>
              <p><strong>Theme:</strong> {detailData.llm_output?.theme?.primary_theme} (Confidence: {detailData.llm_output?.theme?.confidence})</p>
              <p><strong>Industry:</strong> {detailData.llm_output?.industry?.primary_industry} (Confidence: {detailData.llm_output?.industry?.confidence})</p>
              
              <h5 className="mt-4">Extracted Content</h5>
              <div className="bg-light p-3 border rounded" style={{maxHeight: '200px', overflowY: 'auto'}}>
                <pre style={{whiteSpace: 'pre-wrap'}}>{detailData.extracted_files_content}</pre>
              </div>
            </div>
          ) : <p>No details found.</p>}
        </Modal.Body>
      </Modal>
    </div>
  );
};

export default AdvancedDashboard;