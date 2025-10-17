import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';

export function ApiDebugger() {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const testEndpoints = async () => {
    setLoading(true);
    setLogs([]);
    
    try {
      addLog('Testing base endpoint...');
      
      // Test 1: Base endpoint
      const baseResponse = await fetch('https://mtln73s5dnhvx2byqvtrymgvve0nixzl.lambda-url.us-east-1.on.aws/');
      addLog(`Base endpoint status: ${baseResponse.status}`);
      
      // Test 2: Health endpoint
      try {
        const healthResponse = await fetch('https://mtln73s5dnhvx2byqvtrymgvve0nixzl.lambda-url.us-east-1.on.aws/health');
        addLog(`Health endpoint status: ${healthResponse.status}`);
      } catch (error) {
        addLog(`Health endpoint error: ${error}`);
      }
      
      // Test 3: API v1 endpoint structure
      try {
        const apiResponse = await fetch('https://mtln73s5dnhvx2byqvtrymgvve0nixzl.lambda-url.us-east-1.on.aws/api/v1/chats/user/test');
        addLog(`API v1 chats endpoint status: ${apiResponse.status}`);
      } catch (error) {
        addLog(`API v1 endpoint error: ${error}`);
      }
      
      // Test 4: Try different POST methods
      try {
        addLog('Testing POST with FormData...');
        const formData = new FormData();
        formData.append('chat_name', 'test');
        formData.append('user_id', 'debug');
        
        const formResponse = await fetch('https://mtln73s5dnhvx2byqvtrymgvve0nixzl.lambda-url.us-east-1.on.aws/api/v1/chats/', {
          method: 'POST',
          body: formData
        });
        addLog(`FormData POST status: ${formResponse.status}`);
      } catch (error: any) {
        addLog(`FormData POST error: ${error.message}`);
      }

      // Test 5: Try POST with JSON body (different approach)
      try {
        addLog('Testing POST with JSON body...');
        const jsonResponse = await fetch('https://mtln73s5dnhvx2byqvtrymgvve0nixzl.lambda-url.us-east-1.on.aws/api/v1/chats/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({
            chat_name: 'test',
            user_id: 'debug'
          })
        });
        addLog(`JSON POST status: ${jsonResponse.status}`);
        if (!jsonResponse.ok) {
          const errorText = await jsonResponse.text();
          addLog(`JSON POST error response: ${errorText.substring(0, 200)}`);
        }
      } catch (error: any) {
        addLog(`JSON POST error: ${error.message}`);
      }

      // Test 7: Try the new GET endpoint for creating chats
      try {
        addLog('Testing GET create endpoint...');
        const getCreateResponse = await fetch('https://mtln73s5dnhvx2byqvtrymgvve0nixzl.lambda-url.us-east-1.on.aws/api/v1/chats/create?chat_name=TestChat&user_id=DebugUser');
        addLog(`GET create status: ${getCreateResponse.status}`);
        if (getCreateResponse.ok) {
          const responseData = await getCreateResponse.json();
          addLog(`GET create success! Chat ID: ${responseData.chat_id}`);
        } else {
          const errorText = await getCreateResponse.text();
          addLog(`GET create error response: ${errorText.substring(0, 200)}`);
        }
      } catch (error: any) {
        addLog(`GET create error: ${error.message}`);
      }
      
      // Test 5: Try with axios using new format
      try {
        addLog('Testing with axios new format...');
        const axiosResponse = await apiClient.post('/api/v1/chats?chat_name=axiosTest&user_id=debug');
        addLog(`Axios new format success: ${axiosResponse.status}`);
        addLog(`Response data: ${JSON.stringify(axiosResponse.data).substring(0, 200)}`);
      } catch (error: any) {
        addLog(`Axios new format error: ${error.message}`);
        if (error.response) {
          addLog(`Error status: ${error.response.status}`);
          addLog(`Error data: ${JSON.stringify(error.response.data)}`);
        }
      }
      
    } catch (error) {
      addLog(`General error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testEndpoints();
  }, []);

  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <h3 className="text-lg font-bold mb-4">API Debug Logs</h3>
      <button 
        onClick={testEndpoints} 
        disabled={loading}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
      >
        {loading ? 'Testing...' : 'Run Tests'}
      </button>
      <div className="bg-black text-green-400 p-4 rounded font-mono text-sm h-64 overflow-y-auto">
        {logs.map((log, index) => (
          <div key={index}>{log}</div>
        ))}
      </div>
    </div>
  );
}