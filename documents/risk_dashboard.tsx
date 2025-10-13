import React from 'react';
import { AlertTriangle, TrendingUp, Shield, FileText, Activity } from 'lucide-react';

export default function RiskDashboard() {
  const riskData = {
    company_id: "NVDA",
    credit_risk: {
      score: 0.825,
      level: "high",
      factors: [
        "High debt-to-equity ratio",
        "Moderate liquidity",
        "Weak interest coverage",
        "Stagnant revenue growth"
      ],
      confidence: 0.85
    },
    market_risk: {
      score: 0.25,
      level: "low",
      factors: [
        "Moderate market volatility",
        "Moderate foreign currency exposure"
      ],
      confidence: 0.8
    },
    operational_risk: {
      score: 0.6,
      level: "high",
      factors: [
        "High process error rate",
        "High supplier concentration risk",
        "Some cybersecurity concerns"
      ],
      confidence: 0.75
    },
    compliance_risk: {
      score: 0.25,
      level: "low",
      factors: [
        "Minor regulatory violation",
        "GDPR compliance gaps"
      ],
      confidence: 0.9
    },
    overall_risk_score: 0.4925,
    overall_risk_level: "medium",
    recommendations: [
      "Urgent: Improve debt-to-equity ratio through debt reduction or equity financing",
      "Enhance cash flow management and working capital optimization",
      "Strengthen IT infrastructure and cybersecurity measures",
      "Implement business continuity and disaster recovery plans",
      "Diversify supplier base to reduce concentration risk"
    ],
    assessment_id: "RA-20251013105254",
    timestamp: "2025-10-13T10:52:54.896697"
  };

  const getRiskColor = (level) => {
    switch(level) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getRiskBg = (level) => {
    switch(level) {
      case 'high': return 'bg-red-50 border-red-200';
      case 'medium': return 'bg-yellow-50 border-yellow-200';
      case 'low': return 'bg-green-50 border-green-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const RiskCard = ({ title, icon: Icon, data }) => (
    <div className={`rounded-lg border-2 p-6 ${getRiskBg(data.level)}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Icon className="w-6 h-6" />
          <h3 className="font-bold text-lg">{title}</h3>
        </div>
        <span className={`px-3 py-1 rounded-full text-white text-sm font-semibold ${getRiskColor(data.level)}`}>
          {data.level.toUpperCase()}
        </span>
      </div>
      
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium">Risk Score</span>
          <span className="text-2xl font-bold">{(data.score * 100).toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full ${getRiskColor(data.level)}`}
            style={{ width: `${data.score * 100}%` }}
          ></div>
        </div>
      </div>

      <div className="mb-3">
        <span className="text-sm font-medium">Confidence: {(data.confidence * 100).toFixed(0)}%</span>
      </div>

      <div>
        <p className="text-sm font-medium mb-2">Key Factors:</p>
        <ul className="text-sm space-y-1">
          {data.factors.map((factor, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-gray-400 mt-1">•</span>
              <span>{factor}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 mb-2">Risk Assessment Report</h1>
              <p className="text-gray-600">Company: <span className="font-semibold text-xl">{riskData.company_id}</span></p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Assessment ID: {riskData.assessment_id}</p>
              <p className="text-sm text-gray-500">{new Date(riskData.timestamp).toLocaleString()}</p>
            </div>
          </div>

          {/* Overall Risk */}
          <div className={`rounded-lg border-2 p-6 mt-6 ${getRiskBg(riskData.overall_risk_level)}`}>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2">Overall Risk Assessment</h2>
                <div className="flex items-center gap-4">
                  <span className="text-4xl font-bold">{(riskData.overall_risk_score * 100).toFixed(1)}%</span>
                  <span className={`px-4 py-2 rounded-full text-white text-lg font-semibold ${getRiskColor(riskData.overall_risk_level)}`}>
                    {riskData.overall_risk_level.toUpperCase()} RISK
                  </span>
                </div>
              </div>
              <Activity className="w-16 h-16 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Risk Categories Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <RiskCard 
            title="Credit Risk" 
            icon={TrendingUp} 
            data={riskData.credit_risk}
          />
          <RiskCard 
            title="Market Risk" 
            icon={Activity} 
            data={riskData.market_risk}
          />
          <RiskCard 
            title="Operational Risk" 
            icon={AlertTriangle} 
            data={riskData.operational_risk}
          />
          <RiskCard 
            title="Compliance Risk" 
            icon={Shield} 
            data={riskData.compliance_risk}
          />
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center gap-3 mb-6">
            <FileText className="w-6 h-6" />
            <h2 className="text-2xl font-bold">Recommendations</h2>
          </div>
          <div className="space-y-4">
            {riskData.recommendations.map((rec, idx) => (
              <div key={idx} className="flex items-start gap-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
                <span className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">
                  {idx + 1}
                </span>
                <p className="text-gray-700 pt-1">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}