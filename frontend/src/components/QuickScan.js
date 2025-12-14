import React from 'react';
import { PlayCircle, RefreshCw } from 'lucide-react';

export default function QuickScan({ url, setUrl, threads, setThreads, handleScan, currentScan }) {
  const isRunning = currentScan?.status === 'running';

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Scan Rapide</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">URL :</label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            disabled={isRunning}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Threads: {threads}
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={threads}
            onChange={(e) => setThreads(parseInt(e.target.value))}
            disabled={isRunning}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>1</span>
            <span>5</span>
            <span>10</span>
          </div>
        </div>
        
        <button
          onClick={handleScan}
          disabled={isRunning || !url}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-400 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-all shadow-md"
        >
          {isRunning ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              <span>Analyse en cours...</span>
            </>
          ) : (
            <>
              <PlayCircle className="w-5 h-5" />
              <span>Analyser</span>
            </>
          )}
        </button>
        
        {isRunning && (
          <div className="space-y-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-cyan-400 to-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${currentScan.progress}%` }}
              />
            </div>
            <p className="text-sm text-gray-600 text-center">{currentScan.progress}%</p>
          </div>
        )}
      </div>
    </div>
  );
}