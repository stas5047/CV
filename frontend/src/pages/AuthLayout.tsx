export function AuthLayout({
  children,
  subtitle,
}: {
  children: React.ReactNode;
  subtitle: string;
}) {
  return (
    <main className="flex min-h-[100dvh] items-center justify-center bg-background px-6 py-6">
      <section className="av-card flex w-full max-w-[400px] animate-auth-slide-up flex-col gap-6 px-5 py-7 sm:px-8 sm:py-9">
        <div className="flex flex-col items-center gap-2.5 text-center">
          <div className="grid h-12 w-12 place-items-center rounded-[13px] bg-primary font-display text-[17px] font-bold text-primary-foreground">
            AV
          </div>
          <h1 className="font-display text-[21px] font-bold leading-tight tracking-tight">AeroVision</h1>
          <p className="max-w-[31ch] text-[13px] leading-snug text-muted-foreground">{subtitle}</p>
        </div>
        {children}
      </section>
    </main>
  );
}
