'use client';

import { useEffect } from 'react';

const DocsPage: React.FC = () => {
  useEffect(() => {
    // Redirect to the MkDocs index.html in /public/docs
    window.location.href = '/docs/index.html';
  }, []);

  return (
    <div>
      <p>Loading documentation...</p>
    </div>
  );
};

export default DocsPage;
