message("-- Configuring GiGi")


set(GiGi_LINK_LIBS ${Boost_LIBRARIES} ${OPENGL_LIBRARIES} ${FREETYPE_LIBRARIES})
if (JPEG_FOUND)
    list(APPEND GiGi_LINK_LIBS ${JPEG_LIBRARIES})
endif ()
if (PNG_FOUND)
    list(APPEND GiGi_LINK_LIBS ${PNG_LIBRARIES})
endif ()
if (TIFF_FOUND)
    list(APPEND GiGi_LINK_LIBS ${TIFF_LIBRARIES})
endif ()

if (WIN32)
    if (MSVC)
        add_definitions(/wd4146 /wd4099 /wd4251 /wd4800 /wd4267 /wd4275
                        /wd4244 /wd4101 /wd4258 /wd4351 /wd4996)
    endif ()
endif ()

add_library(GiGi
    AlignmentFlags.cpp
    Base.cpp
    BrowseInfoWnd.cpp
    Button.cpp
    ClrConstants.cpp
    Control.cpp
    Cursor.cpp
    DrawUtil.cpp
    DropDownList.cpp
    DynamicGraphic.cpp
    Edit.cpp
    EventPump.cpp
    Font.cpp
    GLClientAndServerBuffer.cpp
    GroupBox.cpp
    GUI.cpp
    Layout.cpp
    ListBox.cpp
    Menu.cpp
    MultiEdit.cpp
    PtRect.cpp
    Scroll.cpp
    ScrollPanel.cpp
    StaticGraphic.cpp
    StyleFactory.cpp
    TabWnd.cpp
    TextControl.cpp
    Texture.cpp
    Timer.cpp
    UnicodeCharsets.cpp
    Wnd.cpp
    WndEvent.cpp
    ZList.cpp

    dialogs/ColorDlg.cpp
    dialogs/FileDlg.cpp
    dialogs/ThreeButtonDlg.cpp

    RichText/RichText.cpp
    RichText/TagParser.cpp
    RichText/ImageBlock.cpp
    RichText/TextBlock.cpp
    RichText/BlockControl.cpp
)

if (USE_STATIC_LIBS)
    set_target_properties(GiGi
        PROPERTIES
        LINK_SEARCH_END_STATIC true
    )
endif ()

target_link_libraries(GiGi ${GiGi_LINK_LIBS})

install(
    TARGETS GiGi
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    COMPONENT COMPONENT_GIGI
)

if (BUILD_DEVEL_PACKAGE)
    install(
        TARGETS GiGi
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        COMPONENT COMPONENT_GIGI_DEVEL
    )
endif ()

if (UNIX AND BUILD_DEVEL_PACKAGE)
    get_pkg_config_libs(pkg_config_libs ${GiGi_LINK_LIBS})

    configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/../cmake/GiGi.pc.in
        ${CMAKE_BINARY_DIR}/GiGi.pc
        @ONLY
    )

    install(
        FILES ${CMAKE_BINARY_DIR}/GiGi.pc
        DESTINATION  ${CMAKE_INSTALL_LIBDIR}/pkgconfig
        COMPONENT COMPONENT_GIGI_DEVEL
        OPTIONAL
    )
endif ()

if (BUILD_SDL_DRIVER)
    add_subdirectory(SDL)
endif ()
