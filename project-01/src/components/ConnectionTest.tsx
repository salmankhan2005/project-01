import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { apiService } from '@/services/api';

export const ConnectionTest = () => {
  const [status, setStatus] = useState('');

  const testConnection = async () => {
    try {
      setStatus('Testing...');
      const result = await apiService.testConnection();
      setStatus(`✅ ${result.message}`);
    } catch (error) {
      setStatus(`❌ ${error instanceof Error ? error.message : 'Connection failed'}`);
    }
  };

  return (
    <div className="p-4 border rounded">
      <Button onClick={testConnection}>Test Backend Connection</Button>
      {status && <p className="mt-2">{status}</p>}
    </div>
  );
};