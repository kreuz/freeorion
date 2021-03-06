cmake_minimum_required(VERSION 2.8.12 FATAL_ERROR)

if(POLICY CMP0044)
    cmake_policy(SET CMP0044 OLD)
endif()

enable_testing()
include(CMakeDependentOption)
include(GNUInstallDirs)

project(GiGi)

########################################
# Configuration                        #
########################################
set(GIGI_VERSION 0.8.0)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_HOME_DIRECTORY}/cmake)

set(MINIMUM_BOOST_VERSION 1.47.0)

option(BUILD_SHARED_LIBS "Enables building of shared libraries; OFF implies static libraries." ON)

cmake_dependent_option(USE_STATIC_LIBS "Favour static linking of depencendies." OFF BUILD_SHARED_LIBS OFF)

if (BUILD_DEBUG)
    set(BUILD_RELEASE OFF)
else ()
    set(BUILD_RELEASE ON)
endif ()

if (DEFINED BUILD_STATIC OR DEFINED BUILD_SHARED)
    message(FATAL "BUILD_STATIC and BUILD_SHARED are removed in favour of BUILD_SHARED_LIBS.")
    return()
endif ()

include(Util)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})


option(BUILD_SDL_DRIVER
       "Builds GG SDL support (the GiGiSDL library)."
       ON)
option(GiGi_BUILD_DOC
       "Builds HTML documentation (requires Doxygen)."
       OFF)
option(BUILD_DEVEL_PACKAGE
       "Install development files."
       ON)

if (NOT DEFINED USE_STATIC_LIBS)
    add_definitions(
        -DBOOST_ALL_NO_LINK
        -DBOOST_ALL_DYN_LINK
        -DBOOST_LOG_DYN_LINK
    )
endif ()

if (MSVC)
    set (CMAKE_STATIC_LIBRARY_PREFIX "lib")
    set (CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} /NODEFAULTLIB:LIBCMT")
    set (CMAKE_STATIC_LINKER_FLAGS "${CMAKE_STATIC_LINKER_FLAGS} /NODEFAULTLIB:LIBCMT")
endif ()

include_directories(${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR})


########################################
# Dependencies                         #
########################################
set(Boost_USE_STATIC_LIBS ${USE_STATIC_LIBS})
find_package(Boost ${MINIMUM_BOOST_VERSION} COMPONENTS chrono date_time filesystem regex signals system thread log REQUIRED)

include_directories(${Boost_INCLUDE_DIRS})

set(int_have_jpeg 0)
set(int_have_png 0)
set(int_have_tiff 0)
find_package(JPEG)
find_package(PNG)
find_package(TIFF)

if (JPEG_FOUND)
    include_directories(${JPEG_INCLUDE_DIR})
    set(int_have_jpeg 1)
endif ()
if (PNG_FOUND)
    include_directories(${PNG_INCLUDE_DIR})
    set(int_have_png 1)
endif ()
if (TIFF_FOUND)
    include_directories(${TIFF_INCLUDE_DIR})
    set(int_have_tiff 1)
endif ()

find_package(OpenGL REQUIRED)
find_package(Freetype REQUIRED)

if (NOT OPENGL_GLU_FOUND)
    message(FATAL_ERROR "OpenGL GLU library not found.")
endif ()

include_directories(
    ${OPENGL_INCLUDE_DIR}
    ${FREETYPE_INCLUDE_DIRS}
)

########################################
# Header Generation                    #
########################################
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/Config.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/GG/Config.h
    @ONLY
)


########################################
# Installed Files                      #
########################################
if (BUILD_DEVEL_PACKAGE)
    install(
        DIRECTORY GG
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        COMPONENT COMPONENT_GIGI_DEVEL
    )
endif ()


########################################
# Recurse Into Sources                 #
########################################
add_subdirectory(src)

########################################
# Documentation                        #
########################################
if (GiGi_BUILD_DOC)
    find_package(Doxygen REQUIRED)
endif ()

if (DOXYGEN_FOUND)
    set(GG_DOC_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/doc")
    set(GG_DOC_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/doc")
    set(GG_DOC_STAMP_DIR "${GG_DOC_OUTPUT_DIR}/GG")
    configure_file(
        ${GG_DOC_SOURCE_DIR}/Doxyfile.in
        ${GG_DOC_OUTPUT_DIR}/Doxyfile
        @ONLY
        IMMEDIATE
    )

    if(NOT TARGET doc)
        add_custom_target(doc)
    endif()

    add_custom_command (
        OUTPUT ${GG_DOC_STAMP_DIR}/index.html
        COMMAND ${DOXYGEN_EXECUTABLE} ${GG_DOC_OUTPUT_DIR}/Doxyfile
        MAIN_DEPENDENCY ${GG_DOC_OUTPUT_DIR}/Doxyfile ${GG_DOC_SOURCE_DIR}/Doxyfile.in
        DEPENDS ${GG_DOC_SOURCE_DIR}/GGDoc.txt
        COMMENT "Generating GiGi API documentation with Doxygen" VERBATIM
    )
    add_custom_target (GiGi-apidoc DEPENDS ${GG_DOC_STAMP_DIR}/index.html)
    add_dependencies(doc GiGi-apidoc)

    if (BUILD_DEVEL_PACKAGE)
        install(
            DIRECTORY ${GG_DOC_STAMP_DIR}
            DESTINATION ${CMAKE_INSTALL_DOCDIR}
        )
    endif ()
endif ()


########################################
# Packaging                            #
########################################
set(CPACK_PACKAGE_VERSION ${GIGI_VERSION})
set(CPACK_PACKAGE_VENDOR "T. Zachary Laine")
set(CPACK_PACKAGE_CONTACT ${CPACK_PACKAGE_VENDOR})
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "A C++ OpenGL GUI library.")
set(CPACK_RESOURCE_FILE_LICENSE ${CMAKE_CURRENT_SOURCE_DIR}/COPYING)
set(CPACK_SYSTEM_NAME ${CMAKE_SYSTEM_NAME})
set(CPACK_PACKAGE_NAME ${CMAKE_PROJECT_NAME})
set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-${CPACK_SYSTEM_NAME}")
set(CPACK_SOURCE_PACKAGE_FILE_NAME ${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-src)

# RPM-specific settings
set(CPACK_RPM_PACKAGE_LICENSE LGPL)
set(CPACK_RPM_PACKAGE_REQUIRES)

list(APPEND CPACK_RPM_PACKAGE_REQUIRES Mesa freetype2)
list(APPEND CPACK_RPM_PACKAGE_REQUIRES gigi=${GIGI_VERSION})

if (BUILD_SDL_DRIVER)
    list(APPEND CPACK_RPM_PACKAGE_REQUIRES SDL>=1.2)
endif ()

if (BUILD_DEVEL_PACKAGE)
    list(APPEND CPACK_RPM_PACKAGE_REQUIRES boost-devel>=1.44.0 Mesa-devel freetype2-devel)
    list(APPEND CPACK_RPM_PACKAGE_REQUIRES gigi-devel=${GIGI_VERSION})
endif ()

if (BUILD_DEVEL_PACKAGE AND BUILD_SDL_DRIVER)
    list(APPEND CPACK_RPM_PACKAGE_REQUIRES SDL-devel>=1.2)
endif ()

# Deb-specific settings
set(CPACK_DEBIAN_PACKAGE_SECTION libs)

set(CPACK_DEBIAN_PACKAGE_DEPENDS "libgl1-mesa-glx | libgl1, libglu1-mesa | libglu, libfreetype6")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "${CPACK_DEBIAN_PACKAGE_DEPENDS}, gigi (= ${GIGI_VERSION})")

if (BUILD_SDL_DRIVER)
    set(CPACK_DEBIAN_PACKAGE_DEPENDS "${CPACK_DEBIAN_PACKAGE_DEPENDS}, libsdl1.2debian (>= 1.2)")
endif ()

if (BUILD_DEVEL_PACKAGE)
    set(CPACK_DEBIAN_PACKAGE_DEPENDS "boost-devel (>= 1.44.0), libgl1-mesa-dev | libgl-dev, libglu1-mesa-dev | libglu-dev, libfreetype6-dev")
    set(CPACK_DEBIAN_PACKAGE_DEPENDS "${CPACK_DEBIAN_PACKAGE_DEPENDS}, gigi-dev (= ${GIGI_VERSION})")
endif ()

if (BUILD_DEVEL_PACKAGE AND BUILD_SDL_DRIVER)
    set(CPACK_DEBIAN_PACKAGE_DEPENDS "${CPACK_DEBIAN_PACKAGE_DEPENDS}, libsdl1.2-dev (>= 1.2)")
endif ()

if (UNIX)
    set(CPACK_GENERATOR "TGZ;TBZ2")
    find_program(RPMBUILD rpmbuild)
    if (RPMBUILD)
        list(APPEND CPACK_GENERATOR RPM)
    endif ()
    set(RPMBUILD ${RPMBUILD} CACHE INTERNAL "")
    find_program(DPKG dpkg)
    if (DPKG)
        list(APPEND CPACK_GENERATOR DEB)
    endif ()
    set(DPKG ${DPKG} CACHE INTERNAL "")
    set(CPACK_SOURCE_GENERATOR "TGZ;TBZ2")
elseif (WIN32)
    set(CPACK_GENERATOR "NSIS")
    set(CPACK_SOURCE_GENERATOR "ZIP")
endif ()

include(CPack)

cpack_add_component(
    COMPONENT_GIGI
    DISPLAY_NAME GiGi
    DESCRIPTION "The core GG library, including the GUI state machine and all the controls.  Not usable without an input driver."
    REQUIRED
    GROUP COMPONENT_GROUP_RUNTIME
)

cpack_add_component(
    COMPONENT_GIGISDL
    DISPLAY_NAME GiGiSDL
    DESCRIPTION "An SDL input driver (http://www.libsdl.org)."
    GROUP COMPONENT_GROUP_RUNTIME
    DEPENDS COMPONENT_GIGI
)

cpack_add_component(
    COMPONENT_GIGI_DEVEL
    DISPLAY_NAME "GiGi"
    DESCRIPTION "The files necessary to do development with GiGi."
    GROUP COMPONENT_GROUP_DEVEL
    DEPENDS COMPONENT_GIGI
)

cpack_add_component(
    COMPONENT_GIGISDL_DEVEL
    DISPLAY_NAME "GiGiSDL"
    DESCRIPTION "The files necessary to do development with GiGiSDL."
    GROUP COMPONENT_GROUP_DEVEL
    DEPENDS COMPONENT_GIGI_DEVEL COMPONENT_GIGISDL
)

cpack_add_component_group(
    COMPONENT_GROUP_RUNTIME
    DISPLAY_NAME "Runtime"
    DESCRIPTION "The runtime libs needed to run an application that uses GG."
    EXPANDED
)

cpack_add_component_group(
    COMPONENT_GROUP_DEVEL
    DISPLAY_NAME "Development"
    DESCRIPTION "The development libs and headers needed to build an application that uses GG."
    EXPANDED
)
