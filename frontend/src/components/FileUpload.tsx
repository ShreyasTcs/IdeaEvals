import React, { useState, useEffect } from 'react';
import { Form } from 'react-bootstrap';

interface FileUploadProps {
  onAdditionalFilesChange: (urls: string[]) => void;
  onIdeasFileChange: (file: File | null) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onAdditionalFilesChange, onIdeasFileChange }) => {
  const [ideasFile, setIdeasFile] = useState<File | null>(null);
  const [additionalFiles, setAdditionalFiles] = useState('');

  useEffect(() => {
    const urls = additionalFiles.split('\n').map(url => url.trim()).filter(url => url.length > 0);
    onAdditionalFilesChange(urls);
  }, [additionalFiles, onAdditionalFilesChange]);

  useEffect(() => {
    onIdeasFileChange(ideasFile);
  }, [ideasFile, onIdeasFileChange]);

  const handleIdeasFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setIdeasFile(event.target.files[0]);
    }
  };

  return (
    <>
      <h3>File Upload</h3>
      <Form>
        <Form.Group className="mb-3" controlId="ideasFile">
          <Form.Label>Ideas File (CSV/XLSX)</Form.Label>
          <Form.Control type="file" accept=".csv,.xlsx" onChange={handleIdeasFileChange} />
          <Form.Text className="text-muted">
            Upload the CSV or XLSX file containing the ideas to be evaluated.
          </Form.Text>
        </Form.Group>


        <Form.Group className="mb-3" controlId="additionalFiles">
          <Form.Label>Additional File URLs</Form.Label>
          <Form.Control
            as="textarea"
            rows={3}
            placeholder="Enter one URL per line"
            value={additionalFiles}
            onChange={(e) => setAdditionalFiles(e.target.value)}
          />
          <Form.Text className="text-muted">
            These URLs should correspond to the additional files already present in the backend data folder.
          </Form.Text>
        </Form.Group>
      </Form>
    </>
  );
};

export default FileUpload;