/*
	When upgrading CKEditor check default config.js for changed toolbarGroups and new additions
*/

CKEDITOR.editorConfig = function (config) {
	config.language = 'en';
	config.contentsCss = ['/static/external/bootstrap-3.3.5/css/bootstrap.min.css','/static/style.css', '/static/external/CKEditor/config/contents.css'];
	
	config.toolbarGroups = [
			{ name: 'clipboard', groups: ['clipboard', 'undo'] },
			{ name: 'editing', groups: ['find', 'selection', 'spellchecker'] },
			{ name: 'links' },
			{ name: 'insert' },
			{ name: 'forms' },
			{ name: 'tools' },
			{ name: 'document', groups: ['mode', 'document', 'doctools'] },
			{ name: 'others' },
			'/',
			{ name: 'basicstyles', groups: ['basicstyles', 'cleanup'] },
			{ name: 'paragraph', groups: ['list', 'indent', 'blocks', 'align', 'bidi'] },
			{ name: 'styles' },
			{ name: 'colors' },
			{ name: 'about' }
	];

	config.stylesSet = [
		{ name: 'Alert - info', element: 'div', attributes: { class: 'alert alert-info' } },
		{ name: 'Alert - success', element: 'div', attributes: { class: 'alert alert-success' } },
		{ name: 'Alert - warning', element: 'div', attributes: { class: 'alert alert-warning' } },
		{ name: 'Alert - danger', element: 'div', attributes: { class: 'alert alert-danger' } },
		{ name: 'Big', element: 'big' },
		{ name: 'Small', element: 'small' },
		{ name: 'Text - muted', element: 'span', attributes: { class: 'text-muted' } },
		{ name: 'Text - primary', element: 'span', attributes: { class: 'text-primary' } },
		{ name: 'Text - info', element: 'span', attributes: { class: 'text-info' } },
		{ name: 'Text - success', element: 'span', attributes: { class: 'text-success' } },
		{ name: 'Text - warning', element: 'span', attributes: { class: 'text-warning' } },
		{ name: 'Text - danger', element: 'span', attributes: { class: 'text-danger' } }
	];

	config.format_tags = 'p;h3;h4;pre';
};
