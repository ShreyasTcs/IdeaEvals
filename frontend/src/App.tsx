import React, { useState } from 'react';
import { Container, Navbar } from 'react-bootstrap';
import './App.css';
import LandingPage from './components/LandingPage';
import HackathonInit from './components/HackathonInit';
import HackathonLogin from './components/HackathonLogin';
import DashboardContainer from './components/DashboardContainer';

type AppView = 'landing' | 'create' | 'login' | 'dashboard';

function App() {
  const [currentView, setCurrentView] = useState<AppView>('landing');
  const [accessCode, setAccessCode] = useState<string | null>(null);

  const handleLoginSuccess = (code: string) => {
    setAccessCode(code);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    setAccessCode(null);
    setCurrentView('landing');
  };

  const renderContent = () => {
    switch (currentView) {
      case 'landing':
        return (
          <LandingPage 
            onStartNew={() => setCurrentView('create')} 
            onViewResults={() => setCurrentView('login')} 
          />
        );
      case 'create':
        return (
          <HackathonInit 
            onBack={() => setCurrentView('landing')} 
          />
        );
      case 'login':
        return (
          <HackathonLogin 
            onLoginSuccess={handleLoginSuccess} 
            onBack={() => setCurrentView('landing')} 
          />
        );
      case 'dashboard':
        return accessCode ? (
          <DashboardContainer 
            accessCode={accessCode} 
            onLogout={handleLogout} 
          />
        ) : (
          // Fallback if state is lost
          <LandingPage onStartNew={() => setCurrentView('create')} onViewResults={() => setCurrentView('login')} />
        );
      default:
        return <div>Unknown State</div>;
    }
  };

  return (
    <>
      <Navbar bg="dark" variant="dark" className="mb-4">
        <Container>
          <Navbar.Brand href="#" onClick={() => setCurrentView('landing')}>
            Hackathon Evaluation System
          </Navbar.Brand>
          {currentView !== 'landing' && (
            <Navbar.Text className="justify-content-end">
              <span className="cursor-pointer" onClick={() => setCurrentView('landing')} style={{cursor: 'pointer'}}>
                Home
              </span>
            </Navbar.Text>
          )}
        </Container>
      </Navbar>
      <Container>
        {renderContent()}
      </Container>
    </>
  );
}

export default App;
