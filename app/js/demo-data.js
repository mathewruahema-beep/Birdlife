// Sample content shown when the live API is unreachable (or demoMode is 'on').
// Clearly generic — real content always comes from birdlife.org.au.

export const DEMO_CATEGORIES = [
  { id: 1, name: 'Conservation' },
  { id: 2, name: 'Campaigns' },
  { id: 3, name: 'Research' },
  { id: 4, name: 'Events' },
];

export const DEMO_POSTS = [
  {
    id: 9001,
    date: '2026-08-18T09:00:00',
    link: 'https://birdlife.org.au/news/',
    title: 'Sample: Spring shorebird counts open for volunteer registration',
    excerpt: '<p>Sample article. When the app can reach birdlife.org.au, live news appears here automatically.</p>',
    content: '<p>This is bundled sample content. The app could not reach the birdlife.org.au API, so it is showing placeholders instead of live articles.</p><p>Once the app is served from a host that can reach the site (or CORS is confirmed), this view fills with the latest posts from the website — no app update required.</p>',
    image: null,
    categories: ['Conservation'],
  },
  {
    id: 9002,
    date: '2026-08-14T09:00:00',
    link: 'https://birdlife.org.au/news/',
    title: 'Sample: Threatened species report highlights woodland birds',
    excerpt: '<p>Sample article demonstrating the reading experience, typography and offline caching.</p>',
    content: '<p>Sample body copy. Articles read cleanly with images, and are cached for offline reading after first view.</p>',
    image: null,
    categories: ['Research'],
  },
  {
    id: 9003,
    date: '2026-08-10T09:00:00',
    link: 'https://birdlife.org.au/news/',
    title: 'Sample: National Bird Week planning underway',
    excerpt: '<p>Sample article in the Campaigns category.</p>',
    content: '<p>Sample body copy for a campaigns article.</p>',
    image: null,
    categories: ['Campaigns'],
  },
];

export const DEMO_EVENTS = [
  {
    id: 9101,
    title: 'Sample: Dawn bird walk — local reserve',
    date: '2026-09-05T06:30:00',
    venue: 'Sample venue',
    link: 'https://birdlife.org.au/events/',
    excerpt: 'Sample event. Live events appear when the site API is reachable.',
  },
  {
    id: 9102,
    title: 'Sample: Beginner bird identification workshop',
    date: '2026-09-12T10:00:00',
    venue: 'Sample venue',
    link: 'https://birdlife.org.au/events/',
    excerpt: 'Sample event entry.',
  },
];
