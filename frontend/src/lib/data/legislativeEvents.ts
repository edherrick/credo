export interface LegislativeEvent {
	id: string;
	date: string; // ISO date "YYYY-MM-DD"
	title: string;
	description: string;
	type: 'bill' | 'rate' | 'policy';
}

export const legislativeEvents: LegislativeEvent[] = [
	{
		id: 'e1',
		date: '2021-03-11',
		type: 'policy',
		title: 'American Rescue Plan',
		description:
			'Federal stimulus injected ~$1.9T into the economy, amplifying housing demand across metro areas.'
	},
	{
		id: 'e2',
		date: '2022-03-16',
		type: 'rate',
		title: 'Fed Rate Hike +0.25%',
		description: 'First Federal Reserve rate increase since 2018, beginning the tightening cycle.'
	},
	{
		id: 'e3',
		date: '2022-06-15',
		type: 'rate',
		title: 'Fed Rate Hike +0.75%',
		description: 'Largest single hike in 28 years — sharply raising mortgage costs nationwide.'
	},
	{
		id: 'e4',
		date: '2023-01-01',
		type: 'bill',
		title: 'IL SB 2038 — ADU Reform',
		description:
			'Illinois bill enabling accessory dwelling units statewide to increase housing supply in urban cores.'
	},
	{
		id: 'e5',
		date: '2023-07-26',
		type: 'rate',
		title: 'Fed Rate Peak 5.25–5.5%',
		description: 'Fed funds rate reaches 22-year high; 30-year mortgage rates exceed 7%.'
	}
];
