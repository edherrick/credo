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

export interface Agenda {
	id: string;
	title: string;
	metric_id: string | null;
	geography_id: string | null;
	direction: 'lower' | 'raise';
	target_value: number | null;
	target_date: string | null;
	status: string;
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
