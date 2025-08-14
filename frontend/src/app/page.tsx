"use client";

import { useState } from "react";
import { useSearchCompanies, useCompare } from "../../lib/hooks";
import { TCompany } from "../../lib/schemas";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCompany, setSelectedCompany] = useState<TCompany | null>(null);

  const { data: companies, isLoading: searchLoading, error: searchError } = useSearchCompanies(searchQuery);
  const { data: comparison, isLoading: compareLoading, error: compareError } = useCompare(selectedCompany?.cvr || "");

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">CVRGPT - Company Search & Analysis</h1>
      
      {/* Search Section */}
      <div className="mb-8">
        <label htmlFor="search" className="block text-sm font-medium mb-2">
          Search for a company:
        </label>
        <input
          id="search"
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Enter company name or CVR..."
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        
        {searchLoading && <p className="mt-2 text-gray-500">Searching...</p>}
        {searchError && <p className="mt-2 text-red-500">Error: {searchError.message}</p>}
        
        {companies && companies.length > 0 && (
          <div className="mt-4 space-y-2">
            <h3 className="font-medium">Results:</h3>
            {companies.map((company) => (
              <button
                key={company.cvr}
                onClick={() => setSelectedCompany(company)}
                className="w-full text-left p-3 border border-gray-200 rounded hover:bg-gray-50 focus:bg-gray-50"
              >
                <div className="font-medium">{company.name}</div>
                <div className="text-sm text-gray-600">CVR: {company.cvr}</div>
                {company.address && <div className="text-sm text-gray-500">{company.address}</div>}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected Company & Comparison */}
      {selectedCompany && (
        <div className="border-t pt-8">
          <h2 className="text-2xl font-semibold mb-4">
            Analysis for {selectedCompany.name}
          </h2>
          
          {compareLoading && <p className="text-gray-500">Loading comparison...</p>}
          {compareError && <p className="text-red-500">Error: {compareError.message}</p>}
          
          {comparison && (
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-lg font-medium mb-4">Financial Comparison</h3>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-2">Current Year ({comparison.a.year})</h4>
                  <div className="space-y-1 text-sm">
                    <div>Revenue: {formatCurrency(comparison.a.revenue)}</div>
                    <div>EBIT: {formatCurrency(comparison.a.ebit)}</div>
                    <div>Equity: {formatCurrency(comparison.a.equity)}</div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium mb-2">Previous Year ({comparison.b.year})</h4>
                  <div className="space-y-1 text-sm">
                    <div>Revenue: {formatCurrency(comparison.b.revenue)}</div>
                    <div>EBIT: {formatCurrency(comparison.b.ebit)}</div>
                    <div>Equity: {formatCurrency(comparison.b.equity)}</div>
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <h4 className="font-medium mb-2">Changes</h4>
                <div className="space-y-1 text-sm">
                  {Object.entries(comparison.deltas).map(([field, delta]) => (
                    <div key={field} className={delta && delta > 0 ? "text-green-600" : delta && delta < 0 ? "text-red-600" : ""}>
                      {field}: {formatCurrency(delta)}
                    </div>
                  ))}
                </div>
              </div>

              {/* Evidence Section */}
              {comparison.citations.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-medium mb-2">Evidence</h4>
                  <div className="space-y-2">
                    {comparison.citations.map((citation, i) => (
                      <a
                        key={i}
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block text-sm text-blue-600 hover:text-blue-800 underline"
                      >
                        {citation.title || citation.url}
                        {citation.retrieved_at && (
                          <span className="text-gray-500 ml-2">
                            (accessed {new Date(citation.retrieved_at).toLocaleDateString()})
                          </span>
                        )}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return "N/A";
  return new Intl.NumberFormat("da-DK", {
    style: "currency",
    currency: "DKK",
    maximumFractionDigits: 0,
  }).format(value);
}