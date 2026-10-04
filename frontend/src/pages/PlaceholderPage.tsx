export function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-center">
      <h1 className="text-3xl font-bold tracking-tight text-text-primary mb-2">{title}</h1>
      <p className="text-text-secondary max-w-sm">
        This section is under construction. It will be implemented in a future phase.
      </p>
    </div>
  );
}
