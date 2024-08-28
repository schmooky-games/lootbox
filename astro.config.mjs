import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'Docs with Tailwind',
			social: {
				github: 'https://github.com/withastro/starlight',
			},
			sidebar: [
				{
					label: 'Общие методы',
					items: [
						'general-methods/get-lootbox',
						'general-methods/get-list-total',
						'general-methods/deactivating-activating',
					],
				},
				{
					label: 'Работа с разными типами лутбоксов',
					items: [
						'lootboxes/equal',
						'lootboxes/weighted',
						'lootboxes/exclusive',
					],
				},
			],
			customCss: ['./src/tailwind.css'],
		}),
		tailwind({ applyBaseStyles: false }),
	],
});
