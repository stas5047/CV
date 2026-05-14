import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listExperiments } from "../api/experiments";
import {
  CompactPerformanceList,
  ConfusionMatrix,
  ChartSectionIcon,
  ExperimentsError,
  ExperimentsHeader,
  ExperimentsSkeleton,
  ExperimentsTabs,
  FalsePositiveSummary,
  MetricCards,
  ModelComparison,
  PerformanceChart,
  SectionEmpty,
  SectionShell,
  ThresholdAnalysis,
  TrackerComparison,
  MixerSectionIcon,
} from "./experiments/ExperimentPageParts";
import {
  EXPERIMENT_EMPTY_TEXT,
  falsePositiveMetrics,
  groupExperiments,
  hasNoSectionData,
  hasSafeConfusionMatrixUrl,
  modelComparisonRows,
  performanceRows,
  precisionRecallCards,
  thresholdRows,
  trackerRows,
} from "./experiments/experimentPageUtils";

type TabId = "models" | "threshold" | "trackers" | "fp";

export function ExperimentsPage() {
  const [tab, setTab] = useState<TabId>("models");
  const experimentsQuery = useQuery({
    queryKey: ["experiments"],
    queryFn: listExperiments,
  });

  const groups = useMemo(
    () => groupExperiments(experimentsQuery.data?.items ?? []),
    [experimentsQuery.data?.items],
  );

  if (experimentsQuery.isLoading) return <ExperimentsSkeleton />;
  if (experimentsQuery.isError) return <ExperimentsError onRetry={() => void experimentsQuery.refetch()} />;

  const noData = hasNoSectionData(groups);
  const comparison = modelComparisonRows(groups.model_comparison);
  const cards = precisionRecallCards(groups.model_comparison);
  const thresholds = thresholdRows(groups.threshold_analysis);
  const trackers = trackerRows(groups.tracker_comparison);
  const performance = performanceRows(groups.model_comparison, groups.tracker_comparison);
  const falsePositives = falsePositiveMetrics(groups.false_positive_analysis);
  const confusionMatrixUrl = hasSafeConfusionMatrixUrl();

  return (
    <div className="space-y-5">
      <ExperimentsHeader />
      <ExperimentsTabs active={tab} onChange={setTab} />

      {noData ? (
        <section className="av-card">
          <SectionEmpty />
        </section>
      ) : null}

      <div className="space-y-5">
        {tab === "models" ? (
          <>
            <SectionShell title="Точність / повнота / mAP" icon={<ChartSectionIcon />}>
              <MetricCards cards={cards} />
            </SectionShell>
            <SectionShell title="Порівняння моделей" icon={<ChartSectionIcon />}>
              <ModelComparison rows={comparison} />
            </SectionShell>
            <SectionShell title="FPS / latency" icon={<ChartSectionIcon />}>
              <PerformanceChart rows={performance} />
              <CompactPerformanceList rows={performance} />
            </SectionShell>
            <SectionShell title="Матриця помилок" icon={<MixerSectionIcon />}>
              <ConfusionMatrix src={confusionMatrixUrl} />
            </SectionShell>
          </>
        ) : null}

        {tab === "threshold" ? (
          <SectionShell title="Поріг впевненості" icon={<ChartSectionIcon />}>
            <ThresholdAnalysis rows={thresholds} />
          </SectionShell>
        ) : null}

        {tab === "trackers" ? (
          <SectionShell title="tracker behavior comparison" icon={<MixerSectionIcon />}>
            <TrackerComparison rows={trackers} />
          </SectionShell>
        ) : null}

        {tab === "fp" ? (
          <SectionShell title="Хибнопозитивний аналіз" icon={<MixerSectionIcon />}>
            <FalsePositiveSummary metrics={falsePositives} />
          </SectionShell>
        ) : null}
      </div>

      <p className="sr-only">{EXPERIMENT_EMPTY_TEXT}</p>
    </div>
  );
}
