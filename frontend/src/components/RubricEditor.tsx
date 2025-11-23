import React, { useState, useEffect } from 'react';
import { Button, Table, Modal, Form, Alert, Spinner } from 'react-bootstrap';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import { Rubric } from '../types';
import { v4 as uuidv4 } from 'uuid';
import defaultRubricsData from '../config/rubrics.json'; // Adjust path as needed
import { generateRubricDescription } from '../api';

interface RubricEditorProps {
  onRubricsChange: (rubrics: Rubric[]) => void;
}

const RubricEditor: React.FC<RubricEditorProps> = ({ onRubricsChange }) => {
  const [rubrics, setRubrics] = useState<Rubric[]>(() =>
    defaultRubricsData.map(r => ({ ...r, id: uuidv4() }))
  );
  const [showModal, setShowModal] = useState(false);
  const [editingRubric, setEditingRubric] = useState<Rubric | null>(null);

  useEffect(() => {
    onRubricsChange(rubrics);
  }, [rubrics, onRubricsChange]);

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination) return;
    const items = Array.from(rubrics);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    setRubrics(items);
  };

  const handleShowModal = (rubric: Rubric | null = null) => {
    setEditingRubric(rubric);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingRubric(null);
  };

  const handleSaveRubric = (rubricData: Omit<Rubric, 'id'> & { id?: string }) => {
    if (editingRubric) {
      setRubrics(rubrics.map(r => (r.id === editingRubric.id ? { ...editingRubric, ...rubricData } : r)));
    } else {
      setRubrics([...rubrics, { ...rubricData, id: uuidv4() }]);
    }
    handleCloseModal();
  };

  const handleDeleteRubric = (id: string) => {
    setRubrics(rubrics.filter(r => r.id !== id));
  };

  return (
    <>
      <h3>Rubric Editor</h3>
      <DragDropContext onDragEnd={handleDragEnd}>
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Weight</th>
              <th>Actions</th>
            </tr>
          </thead>
          <Droppable droppableId="rubrics">
            {(provided) => (
              <tbody {...provided.droppableProps} ref={provided.innerRef}>
                {rubrics.map((rubric, index) => (
                  <Draggable key={rubric.id} draggableId={rubric.id} index={index}>
                    {(provided) => (
                      <tr ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps}>
                        <td>{index + 1}</td>
                        <td>{rubric.name}</td>
                        <td>{rubric.weight * 100}%</td>
                        <td>
                          <Button variant="outline-primary" size="sm" onClick={() => handleShowModal(rubric)}>Edit</Button>{' '}
                          <Button variant="outline-danger" size="sm" onClick={() => handleDeleteRubric(rubric.id)}>Delete</Button>
                        </td>
                      </tr>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </tbody>
            )}
          </Droppable>
        </Table>
      </DragDropContext>
      <Button variant="secondary" onClick={() => handleShowModal()}>Add Rubric</Button>

      <RubricModal
        show={showModal}
        handleClose={handleCloseModal}
        handleSave={handleSaveRubric}
        rubric={editingRubric}
      />
    </>
  );
};

interface RubricModalProps {
  show: boolean;
  handleClose: () => void;
  handleSave: (rubricData: Omit<Rubric, 'id'> & { id?: string }) => void;
  rubric: Rubric | null;
}

const RubricModal = ({ show, handleClose, handleSave, rubric }: RubricModalProps) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [weight, setWeight] = useState(0);
  const [scoringScale, setScoringScale] = useState('');
  const [isGeneratingDescription, setIsGeneratingDescription] = useState(false);

  React.useEffect(() => {
    if (rubric) {
      setName(rubric.name);
      setDescription(rubric.description);
      setWeight(rubric.weight);
      setScoringScale(rubric.scoring_scale_anchor);
    } else {
      setName('');
      setDescription('');
      setWeight(0.1);
      setScoringScale('9–10 Outstanding | 7–8 Strong | 5–6 Fair | 3–4 Weak | 1–2 Poor');
    }
  }, [rubric]);

  const onSave = () => {
    handleSave({ name, description, weight, scoring_scale_anchor: scoringScale });
  };

  const handleGenerateDescription = async () => {
    if (!name) {
      alert('Please enter a rubric name before generating a description.');
      return;
    }
    setIsGeneratingDescription(true);
    try {
      const generated = await generateRubricDescription(name);
      if (generated) {
        setDescription(generated);
      }
    } catch (error) {
      console.error('Failed to generate description:', error);
      alert('Failed to generate description. Check console for details.');
    } finally {
      setIsGeneratingDescription(false);
    }
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>{rubric ? 'Edit' : 'Add'} Rubric</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Name</Form.Label>
            <Form.Control type="text" value={name} onChange={(e) => setName(e.target.value)} />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control as="textarea" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
            <Button variant="link" size="sm" onClick={handleGenerateDescription} disabled={isGeneratingDescription || !name}>
              {isGeneratingDescription ? <Spinner animation="border" size="sm" /> : 'AI Generate'}
            </Button>
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Weight</Form.Label>
            <Form.Control
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={weight}
              onChange={(e) => {
                const value = parseFloat(e.target.value);
                setWeight(isNaN(value) ? 0 : value);
              }}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Scoring Scale Anchor</Form.Label>
            <Form.Control type="text" value={scoringScale} onChange={(e) => setScoringScale(e.target.value)} />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>Close</Button>
        <Button variant="primary" onClick={onSave}>Save Changes</Button>
      </Modal.Footer>
    </Modal>
  );
};

export default RubricEditor;