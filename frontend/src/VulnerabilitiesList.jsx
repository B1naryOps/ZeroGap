
import { useState } from "react";
import ExplanationModal from "./ExplanationModal";

export default function VulnerabilitiesList({ vulns }) {
  const [selectedVuln, setSelectedVuln] = useState(null);

  return (
    <div>
      {vulns.map((v) => (
        <div key={v.id} className="border p-4 rounded-lg mb-3">
          <h3 className="font-bold">{v.name}</h3>
          <p className="text-sm text-gray-600">{v.description}</p>

          {/* Bouton expliquer */}
          <button
            onClick={() => setSelectedVuln(v)}
            className="mt-2 px-4 py-1 bg-blue-600 text-white rounded-md"
          >
            Expliquer
          </button>
        </div>
      ))}

      {/* Modal */}
      <ExplanationModal
        isOpen={selectedVuln !== null}
        onClose={() => setSelectedVuln(null)}
        vuln={selectedVuln}
      />
    </div>
  );
}
