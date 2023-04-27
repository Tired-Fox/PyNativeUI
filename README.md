# PyNativeUI 

<!-- Header Badges -->

<div align="center">
  
<img src="assets/badges/version.svg" alt="Version"/>
<a href="https://github.com/Tired-Fox/PyNativeUI/releases" alt="Release"><img src="https://img.shields.io/github/v/release/tired-fox/PyNativeUI.svg?style=flat-square&color=9cf"/></a>
<a href="https://github.com/Tired-Fox/PyNativeUI/blob/main/LICENSE" alt="License"><img src="assets/badges/license.svg"/></a>
<img src="assets/badges/maintained.svg" alt="Maintained"/>
<br>
<img src="assets/badges/tests.svg" alt="Tests"/>
<img src="assets/badges/coverage.svg" alt="Coverage"/>
  
</div>

<!-- End Header -->

## Structure
```
native_ui
- core/
- kit/
  - integrate.py
  - mac/
  - linux/
  - window/
```

The core of native ui is to allow for generic application generation with the same syntax regardless of the
platform. The idea is provide a pythonic way of defining an element and object structure. Styles are names and use the same syntax as css. They can either be defined in a dict or in a css file itself. Below this higher layer of objects and styles are the base kits. The kits directly interface with 3 main API's. Mac's Objective C, Window's Win32 API, and Linux's GTK API.

## Steps

1. data → characters → Tokens → 1
2. 1? → DOM/Object Model → Render Tree → OS API Calls

The idea is that you get some source that creates and AST/DOM. From there the elements and styles
are combined into a render tree. From the render tree the layout is calculated. After all data is calculated
OS API Calls are made and the application is rendered.

It will require that the DOM and Render tree are recalculated and rerendered on window resize. Otherwise each element will have it's own rendering for different states.

## Configuration

Configuration will need to be provided to specify icons and other base data like starting window size.


## References
[PyWin32](http://timgolden.me.uk/pywin32-docs/win32_modules.html)
[stackoverflow](https://stackoverflow.com/a/68029095) referencing [acrylic composition example](https://github.com/Extrimis/Win32-Acrylic-Effect/blob/master/Acrylic%Q/Acrylic%20Window.cpp)

[LogRocket](https://blog.logrocket.com/how-browser-rendering-works-behind-scenes/) blog on how browsers work
WebKit [WebCore Rendering](https://webkit.org/blog/114/webcore-rendering-i-the-basics/)

[Win32 Control Libarary](https://learn.microsoft.com/en-us/windows/win32/controls/individual-control-info)
  - Research on how to use all of the controls
  - Research on how the controls can be customized
  - Research on how the custom controls can be created

<!-- Footer Badges --!>

<br>
<div align="center">
  <img src="assets/badges/made_with_python.svg" alt="Made with python"/>
  <img src="assets/badges/built_with_love.svg" alt="Built with love"/>
</div>

<!-- End Footer -->
