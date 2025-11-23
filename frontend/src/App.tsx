import React from 'react';
import { Container, Navbar } from 'react-bootstrap';
import './App.css';
import EvaluationSetup from './components/EvaluationSetup';

function App() {
  return (
    <>
      <Navbar bg="dark" variant="dark">
        <Container>
          <Navbar.Brand href="#home">Hackathon Evaluation</Navbar.Brand>
        </Container>
      </Navbar>
      <Container className="mt-4">
        <EvaluationSetup />
      </Container>
    </>
  );
}

export default App;
