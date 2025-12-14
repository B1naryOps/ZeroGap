import React from 'react';
import { Shield, AlertTriangle, FileText } from 'lucide-react';

export default function StatisticsPanel({ statistics }) {
  if (!statistics) return null;

  return (
    <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-md p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm opacity-90">Total Scans</p>
            <p className="text-3xl font-bold mt-1">{statistics.total_scans}</p>
          </div>
          <Shield className="w-10 h-10 opacity-50" />
        </div>
      </div>
      
      <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg shadow-md p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm opacity-90">Vulnérabilités</p>
            <p className="text-3xl font-bold mt-1">{statistics.total_vulnerabilities}</p>
          </div>
          <AlertTriangle className="w-10 h-10 opacity-50" />
        </div>
      </div>
      
      <div className="bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-lg shadow-md p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm opacity-90">Moyenne/Scan</p>
            <p className="text-3xl font-bold mt-1">{statistics.average_vulnerabilities_per_scan}</p>
          </div>
          <FileText className="w-10 h-10 opacity-50" />
        </div>
      </div>
    </div>
  );
}