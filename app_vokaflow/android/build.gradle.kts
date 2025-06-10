allprojects {
    repositories {
        google()
        mavenCentral()
    }
    
    // Suppress Java warnings globally
    tasks.withType<JavaCompile>().configureEach {
        options.compilerArgs.addAll(listOf(
            "-Xlint:-options",
            "-Xlint:-unchecked", 
            "-Xlint:-deprecation",
            "-Xlint:-rawtypes"
        ))
        options.isWarnings = false
    }
    
    // Force Java 11 for all subprojects
    plugins.withType<JavaPlugin>() {
        configure<JavaPluginExtension> {
            sourceCompatibility = JavaVersion.VERSION_11
            targetCompatibility = JavaVersion.VERSION_11
        }
    }
}

val newBuildDir: Directory = rootProject.layout.buildDirectory.dir("../../build").get()
rootProject.layout.buildDirectory.value(newBuildDir)

subprojects {
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
}
subprojects {
    project.evaluationDependsOn(":app")
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
