import { useEffect } from 'react';
import { useResumeStore } from './store/resume-store';
import { loadResumeYaml } from './utils/yaml-loader';
import TopNav from './components/layout/TopNav';
import Sidebar from './components/layout/Sidebar';
import ContentEditor from './components/editor/ContentEditor';
import PreviewPanel from './components/layout/PreviewPanel';
import './index.css';

function App() {
  const { setResumeData, setLoading, setError, isLoading, error, previewOpen } =
    useResumeStore();

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await loadResumeYaml();
        setResumeData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resume data');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [setResumeData, setLoading, setError]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">Loading resume data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <TopNav />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <ContentEditor />
        {previewOpen && <PreviewPanel />}
      </div>
    </div>
  );
}

export default App;
