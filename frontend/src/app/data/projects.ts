export type Project = {
  name: string;
  year: string;
  desc: string;
  tags: string[];
  links: { label: string; href: string }[];
};

export const PROJECTS: Project[] = [
  {
    name: 'RAG Portfolio Assistant',
    year: '2026',
    desc: "Custom ingestor, embedding pipeline, and retrieval service powering this portfolio's AI chatbot.",
    tags: ['Python', 'RAG', 'FastAPI'],
    links: [{ label: 'GitHub', href: '#' }, { label: 'Live', href: '#' }],
  },
  {
    name: 'LLM Fine-tuning Toolkit',
    year: '2025',
    desc: 'Domain-specific model adaptation with evaluation benchmarks and reproducible training configs.',
    tags: ['PyTorch', 'Hugging Face', 'LoRA'],
    links: [{ label: 'GitHub', href: '#' }],
  },
  {
    name: 'Document Ingestor Service',
    year: '2025',
    desc: 'Multi-format document parser with chunking strategies and metadata extraction for vector stores.',
    tags: ['Python', 'PDF', 'Vector DB'],
    links: [{ label: 'GitHub', href: '#' }],
  },
  {
    name: 'Computer Vision Pipeline',
    year: '2024',
    desc: 'Object detection and classification pipeline for real-world image datasets with inference API.',
    tags: ['OpenCV', 'YOLO', 'FastAPI'],
    links: [{ label: 'GitHub', href: '#' }],
  },
];
