# Research-Question Field Matrix

The machine-readable source is `protocol/v1/rq-field-map.json`; tests resolve every listed path against a v1 schema. Paths below omit `meta`, which supplies identity, digest, provenance, validity, status, and scientific disposition for every record.

| Question / output | Experimental unit and admission | Concrete stored fields |
|---|---|---|
| RQ1 CPU affinity, B1/B0 | Independent accepted run pair; `A_B1j*A_B0j*E_mem_j=1` | `AcceptanceRecord.payload.A_bj`; `PageEquivalenceRecord.payload.state`, `mandatory_object_join[*].d_tv`, `tau_mem`; `AggregatedDataset.payload.adjacent_pair_indicators[*].A_1_0`; per-run `runs[*].quantiles.p999`; `StatisticalAnalysisArtifact.payload.key_secondary.rq1_b1_b0.{accepted_pair_ids,mean_log_ratio,absolute_difference,raw_p_value,holm_adjusted_p_value}` |
| RQ2 memory binding, B2/B1 | Independent accepted run pair; `A_B2j*A_B1j=1` | `CPUAccessProfile.payload.objects[*].accessors[*].demand_share`; `LocationQualifiedObject.payload.{desired_distribution,requested_policy,observed_distribution}`; `AggregatedDataset.payload.adjacent_pair_indicators[*].A_2_1`; per-run p99.9; `key_secondary.rq2_b2_b1` effect, absolute difference, and Holm fields |
| RQ3 complete placement, B3/B2 | Sole-primary independent accepted run pair at frozen `l*`; `A_B3j*A_B2j=1` | `AggregatedDataset.payload.adjacent_pair_indicators[*].A_3_2`; `StatisticalAnalysisArtifact.payload.primary.{estimand_label,reference_condition_id,accepted_pair_ids,D_j,mean_D,standard_error,t_statistic,one_sided_p_value,upper_one_sided_95_bound,two_sided_95_lower,two_sided_95_upper,transformed_relative_effect,planned_pair_count,accepted_pair_count,decision}` |
| RQ4 workload dependence | Blocked adjacent-pair effects; secondary/predeclared interactions | `WorkloadSpec.payload.{packet_bytes,resolved_packet_rate,burst_model,flow_distribution,queue_count,worker_count}`; `StatisticalAnalysisArtifact.payload.secondary_analyses.rq4_interactions[*].{factor,incremental_contrast,estimate,interval_lower,interval_upper,analysis_family}` |
| RQ5 model explanation | Complete accepted calibration/mechanism runs; term-family correction | `CostTermValue.payload.{term_id,physical_mechanism,owner_group,normalized_value,component_weight,group_coefficient}`; `PlacementPlan.payload.{assignments,cost_terms,total_score}`; `TelemetryRecord.payload.extended_value`; model coefficients and seen/unseen validation; `secondary_analyses.rq5_model_explanation[*].{term_or_group_id,ablation_plan_digest,placement_changed,p999_effect,goodput_effect,counter_association,held_out_rank,family_label}` |
| RQ6 stability | Declared workload/topology/frontend replication, not another packet/run repetition | `TopologySnapshot.payload.snapshot_id`; model validity and unseen-condition validation; `secondary_analyses.rq6_stability[*].{change_id,change_class,policy_rank_correlation,candidate_cost_rank_correlation,top_choice_accuracy,regret,validity_domain_result}` |

## Sole-primary and key-secondary outputs

The sole-primary output is the conditional B3/B2 mean log ratio at `l*`, its transformed relative effect, standard error, paired-t statistic, one-sided p-value, aligned upper one-sided 95% bound, two-sided 95% Student interval, fixed planned/accepted pair counts, diagnostics, and decision. All are under `StatisticalAnalysisArtifact.payload.primary`; none may be populated from packet-level repetitions.

RQ1 and RQ2 are the only key-secondary testing family. Their accepted pair IDs, log-ratio effect, absolute difference, raw p-value, and Holm-adjusted p-value live under `payload.key_secondary`. Direct B3/B0, p99.99, interactions, ablations, and robustness outputs remain secondary/exploratory.

## Co-constraints and attrition

| Required output | Concrete fields |
|---|---|
| Run-level percentile inputs | `AggregatedDataset.payload.runs[*].{valid_observation_count,quantiles,nearest_rank_indices,correctness_digest,scientifically_excluded,source_record_digests}` |
| Policy attempt acceptance `A_bj` | `AcceptanceRecord.payload.A_bj`; `AggregatedDataset.payload.runs[*].A_bj` |
| Page-equivalence `E_mem,j` | `AggregatedDataset.payload.page_equivalence_records[*].{state,E_mem_j,record_digest}` |
| Adjacent indicators | `AggregatedDataset.payload.adjacent_pair_indicators[*].{A_1_0,A_2_1,A_3_2,pair_record_ids}` |
| Policy/pair attrition | `AggregatedDataset.payload.attrition[*].{policy_or_pair,planned_count,attempted_count,accepted_count,failure_category,failure_count,failure_rate,incomplete_block_policy}` |
| Operational feasibility | `StatisticalAnalysisArtifact.payload.operational_feasibility` |
| Scientific exclusion | `meta.scientific_disposition`; `AggregatedDataset.payload.runs[*].scientifically_excluded` |

Within-run N and uncertainty do not change the independent unit. A packet count supports a run-level tail estimate; it does not increase the number of independent repetitions.
