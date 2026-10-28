import { useEffect, useState } from 'react';
import { getHealth } from '../api/api';

type ConnectionStatus =
  | 'checking'
  | 'connected'
  | 'error';

function ApiStatus() {
  const [status, setStatus] =
    useState<ConnectionStatus>('checking');

  useEffect(() => {
    async function checkApi() {
      try {
        const result = await getHealth();

        if (result.status === 'healthy') {
          setStatus('connected');
        } else {
          setStatus('error');
        }
      } catch {
        setStatus('error');
      }
    }

    checkApi();
  }, []);

  if (status === 'checking') {
    return <span>API: Checking...</span>;
  }

  if (status === 'connected') {
    return <span>API: Connected</span>;
  }

  return <span>API: Unavailable</span>;
}

export default ApiStatus;