import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() => runApp(const TalaltamApp());

class TalaltamApp extends StatelessWidget {
  const TalaltamApp({super.key});

  @override
  Widget build(BuildContext context) {
    const ink = Color(0xFF18212F);
    const teal = Color(0xFF12A895);
    return MaterialApp(
      title: 'Találtam',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: teal, brightness: Brightness.light),
        scaffoldBackgroundColor: const Color(0xFFF5F7F8),
        appBarTheme: const AppBarTheme(backgroundColor: Color(0xFFF5F7F8), foregroundColor: ink, elevation: 0),
        cardTheme: CardThemeData(color: Colors.white, elevation: 0, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18))),
        inputDecorationTheme: InputDecorationTheme(
          filled: true, fillColor: Colors.white,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none),
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
