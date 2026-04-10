export interface Geography {
	id: string;
	name: string;
	state_fips: string;
	geo_type: string;
}

export interface Metric {
	id: string;
	display_name: string;
	unit: string;
	description: string | null;
	data_source: string | null;
}

export interface MetricValuePoint {
	period_start: string;
	period_end: string | null;
	value: number;
}

export interface MetricValuesResponse {
	metric_id: string;
	geography_id: string;
	unit: string;
	values: MetricValuePoint[];
}

export type MeansCategory =
	| 'incentive'
	| 'penalty'
	| 'mandate'
	| 'boycott'
	| 'divestment'
	| 'zoning'
	| 'litigation'
	| 'petition'
	| 'subsidy';

export interface AgendaMeans {
	id: string;
	category: MeansCategory;
	title: string;
	description: string | null;
	target: string | null;
}

export interface Agenda {
	id: string;
	title: string;
	metric_id: string | null;
	credo_id: string | null;
	geography_ids: string[];
	direction: 'lower' | 'raise';
	target_value: number | null;
	target_date: string | null;
	status: string;
	means: AgendaMeans[];
}

export interface EntityEvent {
	id: string;
	title: string;
	description: string | null;
	event_date: string | null;
	metric_id: string | null;
	event_impact_score: number | null;
	source_url: string | null;
	source_type: string;
}

export interface Entity {
	id: string;
	name: string;
	type: string;
	description: string | null;
	impact_score: number; // credo-specific score
	events: EntityEvent[];
}

export interface Credo {
	id: string;
	username: string;
	title: string;
	description: string | null;
	agendas: Agenda[];
	entities: Entity[];
}

export interface User {
	id: string;
	email: string;
	username: string | null;
	display_name: string | null;
	created_at: string;
}

export interface AuthToken {
	access_token: string;
	token_type: string;
}

export interface CountySeries {
	id: string;
	name: string;
	values: (number | null)[];
}

export interface MetricAggregateResponse {
	metric_id: string;
	dates: string[];
	avg_values: number[];
	counties: CountySeries[];
}

export interface MetricSeries {
	metricId: string;
	label: string;
	dates: string[];
	avgValues: (number | null)[];
}
