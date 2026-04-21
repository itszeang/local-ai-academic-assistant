import { BookOpen, Brain, FileQuestion, FileText, Layers, ListChecks, MessageSquareText, Scale } from "lucide-react";

import type { GenerateMode } from "../../services/api";

export type ProductMode = "study" | "academic";
export type StudyTask = "quick_qa" | "flashcards" | "quiz";
export type AcademicTask = "academic_qa" | "summarize" | "argument" | "literature_review";
export type TaskId = StudyTask | AcademicTask;

export type TaskConfig = {
  id: TaskId;
  productMode: ProductMode;
  label: string;
  shortLabel: string;
  description: string;
  primaryAction: string;
  promptLabel: string;
  promptPlaceholder: string;
  backendMode?: GenerateMode;
  requiresEvidencePanel: boolean;
  isImplemented: boolean;
  examplePrompts: string[];
  icon: typeof MessageSquareText;
};

export const STUDY_TASKS: TaskConfig[] = [
  {
    id: "quick_qa",
    productMode: "study",
    label: "Quick Q&A",
    shortLabel: "Quick Q&A",
    description: "Ask a focused question and get a short answer from your selected notes.",
    primaryAction: "Ask from Notes",
    promptLabel: "What do you want to understand?",
    promptPlaceholder: "Example: Explain Scrum in simple terms.",
    backendMode: "qa",
    requiresEvidencePanel: false,
    isImplemented: true,
    examplePrompts: [
      "Explain this topic simply.",
      "What should I remember for the exam?",
      "What are the most important points in this lecture?"
    ],
    icon: Brain
  },
  {
    id: "flashcards",
    productMode: "study",
    label: "Generate Flashcards",
    shortLabel: "Flashcards",
    description: "Turn selected notes into review cards. Planned for the next study iteration.",
    primaryAction: "Create Flashcards",
    promptLabel: "Flashcard focus",
    promptPlaceholder: "Example: Create flashcards for agile roles.",
    requiresEvidencePanel: false,
    isImplemented: false,
    examplePrompts: ["Turn this topic into flashcards.", "Create terms and definitions from this PDF."],
    icon: Layers
  },
  {
    id: "quiz",
    productMode: "study",
    label: "Generate Quiz",
    shortLabel: "Quiz",
    description: "Create practice questions from your notes. Visible now, wired in V2.",
    primaryAction: "Create Quiz",
    promptLabel: "Quiz focus",
    promptPlaceholder: "Example: Ask me 5 practice questions from this PDF.",
    requiresEvidencePanel: false,
    isImplemented: false,
    examplePrompts: ["Ask me 5 practice questions.", "Create a short test from this lecture."],
    icon: ListChecks
  }
];

export const ACADEMIC_TASKS: TaskConfig[] = [
  {
    id: "academic_qa",
    productMode: "academic",
    label: "Answer a Question",
    shortLabel: "Answer",
    description: "Ask a document-grounded academic question with visible evidence.",
    primaryAction: "Generate Answer",
    promptLabel: "Academic question",
    promptPlaceholder: "Example: What is the main argument of this paper?",
    backendMode: "qa",
    requiresEvidencePanel: true,
    isImplemented: true,
    examplePrompts: [
      "What is the main argument of this paper?",
      "Which evidence supports Scrum adoption?",
      "What limitation does the selected document mention?"
    ],
    icon: FileQuestion
  },
  {
    id: "summarize",
    productMode: "academic",
    label: "Summarize Document",
    shortLabel: "Summarize",
    description: "Produce a structured academic summary of the selected sources.",
    primaryAction: "Summarize",
    promptLabel: "Summary instruction",
    promptPlaceholder: "Example: Summarize the selected document in 5 key points.",
    backendMode: "summarization",
    requiresEvidencePanel: true,
    isImplemented: true,
    examplePrompts: [
      "Summarize the selected document in a structured academic format.",
      "Extract the main findings and key concepts.",
      "Summarize this source for literature notes."
    ],
    icon: FileText
  },
  {
    id: "argument",
    productMode: "academic",
    label: "Build an Argument",
    shortLabel: "Argument",
    description: "Create a thesis, support, and counterargument structure from evidence.",
    primaryAction: "Build Argument",
    promptLabel: "Argument goal",
    promptPlaceholder: "Example: Build an argument for Scrum adoption using this source.",
    backendMode: "argument_builder",
    requiresEvidencePanel: true,
    isImplemented: true,
    examplePrompts: [
      "Build an argument for adopting Scrum using the selected source.",
      "Create a position with supporting evidence.",
      "What counterargument is supported by the document?"
    ],
    icon: Scale
  },
  {
    id: "literature_review",
    productMode: "academic",
    label: "Literature Review",
    shortLabel: "Review",
    description: "Synthesize themes, gaps, and evidence across selected academic documents.",
    primaryAction: "Generate Literature Review",
    promptLabel: "Review focus",
    promptPlaceholder: "Example: Create a literature review style synthesis from the selected documents.",
    backendMode: "literature_review",
    requiresEvidencePanel: true,
    isImplemented: true,
    examplePrompts: [
      "Create a literature review style synthesis from the selected documents.",
      "Compare the themes across the selected sources.",
      "Identify research gaps supported by these documents."
    ],
    icon: BookOpen
  }
];

export const TASKS = [...STUDY_TASKS, ...ACADEMIC_TASKS];

export function taskById(taskId: TaskId): TaskConfig {
  const task = TASKS.find((candidate) => candidate.id === taskId);
  if (!task) {
    throw new Error(`Unknown task: ${taskId}`);
  }
  return task;
}
