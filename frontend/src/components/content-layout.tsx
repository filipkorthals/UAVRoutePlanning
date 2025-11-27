const ContentLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="grid font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-row row-start-2 items-center sm:items-start">
        {children}
      </main>
    </div>
  );
};

export default ContentLayout;
