# Directory Structure

Aerobatic defaults to some specific common front-end conventions. By conforming to these conventions you can simplify your configuration (convention over configuration).

Here is the basic suggested skeleton for your app repo that each of the starter templates conforms to:

```bash
├── app
│   ├── css
│   │   ├── **/*.css
│   ├── favicon.ico
│   ├── images
│   ├── index.html
│   ├── js
│   │   ├── **/*.js
│   └── partials/template
├── dist (or build)
├── node_modules
├── bower_components (if using bower)
├── test
├── Gruntfile.js/gulpfile.js
├── README.md
├── package.json
├── bower.json (if using bower)
└── .gitignore
```

Your app's source code is nested beneath the `app` directory. This is where assets are served from in `debug` mode. Note that in most cases it is not necessary to setup a watch to re-compile languages and syntaxes including CoffeeScript, Sass, Stylus, Jade, and LESS as the development server will automatically do this for you in middleware. Note that in your index page, you should not include the `/app` prefix since the development asset server will treat it as the root.

```html
<!- Serves app/js/main.js-->
<script data-aero-build="debug" src="/js/main.js"></script>
```

For deployment, `yoke` assumes that all the files (including the index page) required to run in `release` mode have been written to a directory called either `dist` or `build` off the root. Grunt or Gulp both have good facilities for writing the outputs of a task to a different directory.

<div>
      <h1>SpirAi YOLO Data Laboratory</h1>
  <div>
    <h3>What is The SpirAi Data Lab?</h3>
    <p>Te library provides Dataset collecting, converting, testing and Model testing on videos, frames, images practically. </p>
  </div>
  <div>
      <details open> 
            <summary>📘 Usage</summary>
            <p>It can be added as a local library or can be used by cloning this repo and importing it with a py file in its parent directory.</p>   
            <p>For dataset processes you can use scripts in datasets folder<, for testing you can use test folder. The models folder is for the YOLO models/p>
       </details>
  </div>
  <div>
      <details open> 
            <summary>🌲 File and Class Hieararchy</summary>
      </details>
  </div>
</div>


