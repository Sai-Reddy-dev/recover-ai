function SkeletonCard() {
  return (
    <div className="card card-pad">
      <div className="flex items-start justify-between">
        <div className="skeleton h-4 w-28" />
        <div className="skeleton h-9 w-9 rounded-lg" />
      </div>
      <div className="skeleton mt-4 h-8 w-32" />
      <div className="skeleton mt-2 h-3 w-40" />
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card card-pad">
          <div className="skeleton h-5 w-44" />
          <div className="skeleton mt-1.5 h-4 w-64" />
          <div className="skeleton mt-6 h-64 w-full" />
        </div>
        <div className="card card-pad">
          <div className="skeleton h-5 w-44" />
          <div className="skeleton mt-1.5 h-4 w-64" />
          <div className="skeleton mt-6 h-64 w-full" />
        </div>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="card card-pad">
            <div className="flex items-center gap-4">
              <div className="skeleton h-10 w-10 rounded-lg" />
              <div>
                <div className="skeleton h-7 w-12" />
                <div className="skeleton mt-2 h-3 w-28" />
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="card card-pad">
        <div className="skeleton h-5 w-40" />
        <div className="skeleton mt-1.5 h-4 w-64" />
        <div className="mt-6 flex flex-col gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="skeleton h-3 w-3 rounded-full" />
              <div className="flex-1">
                <div className="skeleton h-4 w-48" />
                <div className="skeleton mt-2 h-3 w-72" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
