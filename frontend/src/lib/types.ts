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

export interface MeansCategory {
	id: string;
	label: string;
	family: string;
	description: string | null;
}

export interface MeansEvidence {
	id: string;
	title: string;
	description: string | null;
	source_url: string | null;
	geography_id: string | null;
	outcome: string | null;
}

export interface Means {
	id: string;
	title: string;
	description: string | null;
	category: MeansCategory;
	canonical: boolean;
	evidence: MeansEvidence[];
}

export interface AgendaMeans {
	means_id: string;
	notes: string | null;
	means: Means;
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

export interface Belief {
	id: string;
	title: string;
	statement: string;
	category: string;
	source: string | null;
	canonical: boolean;
}

export interface CredoBelief {
	belief: Belief;
	display_order: number;
	notes: string | null;
}

export interface Axis {
	id: string;
	label: string;
	description: string | null;
	family: string;
	canonical: boolean;
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

export interface EntityDetail {
	id: string;
	name: string;
	slug: string | null;
	type: string;
	description: string | null;
	wikidata_id: string | null;
	events: EntityEvent[];
}

export interface Credo {
	id: string;
	username: string;
	title: string;
	description: string | null;
	owner_id: string | null; // null = platform-seeded / unowned
	beliefs: CredoBelief[];
	agendas: Agenda[];
	entities: Entity[];
}

export interface CredoSummary {
	id: string;
	username: string;
	title: string;
	description: string | null;
	owner_id: string | null; // null = platform-seeded / unowned
	created_at: string;
}

// Write payloads — mirror the backend CredoCreate / CredoUpdate schemas.
export interface CredoCreateInput {
	username: string; // public handle / URL slug
	title: string;
	description?: string | null;
}

export interface CredoUpdateInput {
	title?: string;
	description?: string | null;
}

export interface Issue {
	id: string;
	title: string;
	description: string | null;
	category: string | null;
	canonical: boolean;
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
