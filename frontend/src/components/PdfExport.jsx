import { useState } from 'react';

export default function PdfExport({ destination }) {
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      const html2canvas = (await import('html2canvas')).default;
      const { jsPDF } = await import('jspdf');
      
      const element = document.querySelector('.itinerary-view');
      if (!element) { alert('No itinerary to export'); return; }

      const canvas = await html2canvas(element, {
        backgroundColor: '#0a0f1a',
        scale: 2,
        useCORS: true,
        logging: false,
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

      let heightLeft = pdfHeight;
      let position = 0;

      pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, pdfHeight);
      heightLeft -= pdf.internal.pageSize.getHeight();

      while (heightLeft > 0) {
        position -= pdf.internal.pageSize.getHeight();
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, pdfHeight);
        heightLeft -= pdf.internal.pageSize.getHeight();
      }

      const filename = `${(destination || 'trip').toLowerCase().replace(/\s+/g, '-')}-itinerary.pdf`;
      pdf.save(filename);
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={loading}
      className="btn btn-secondary"
      style={{ fontSize: '0.82rem', padding: '7px 16px', gap: '6px' }}
    >
      {loading ? (
        <><div className="spinner" style={{ width: 14, height: 14 }} /> Generating...</>
      ) : (
        <>📄 Download PDF</>
      )}
    </button>
  );
}
