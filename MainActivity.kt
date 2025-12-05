class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        Python.start(AndroidPlatform(this))
        val py = Python.getInstance()
        py.getModule("run_django")

        // WebView cargando Django local
        val web = WebView(this)
        web.settings.javaScriptEnabled = true
        web.loadUrl("http://127.0.0.1:8000/")
        setContentView(web)
    }
}
